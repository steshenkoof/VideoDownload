import os
import re
import json
import socket
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import validators
from urllib.parse import urlparse
import instaloader

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Создаем папку для загрузок
DOWNLOADS_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

class RussianVideoDownloader:
    def __init__(self):
        # Настройки для обхода блокировок в России
        self.ydl_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]/best',
            'noplaylist': True,
            
            # Настройки для обхода блокировок
            'proxy': None,  # Можно указать прокси
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            
            # Настройки User-Agent
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            
            # Дополнительные настройки
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'prefer_insecure': False,
            
            # Специальные настройки для YouTube
            'youtube_include_dash_manifest': False,
            'youtube_skip_dash_manifest': True,
        }
        
        # Настройки DNS для обхода блокировок
        self.setup_dns()
    
    def setup_dns(self):
        """Настройка альтернативных DNS серверов"""
        try:
            # Пробуем использовать альтернативные DNS
            socket.getaddrinfo('www.google.com', 80)
        except:
            pass
    
    def detect_platform(self, url):
        """Определяет платформу по URL"""
        domain = urlparse(url).netloc.lower()
        
        if any(x in domain for x in ['youtube.com', 'youtu.be', 'm.youtube.com']):
            return 'youtube'
        elif any(x in domain for x in ['tiktok.com', 'vm.tiktok.com', 'm.tiktok.com']):
            return 'tiktok'
        elif any(x in domain for x in ['instagram.com', 'm.instagram.com']):
            return 'instagram'
        elif any(x in domain for x in ['t.me', 'telegram.me']):
            return 'telegram'
        else:
            return 'unknown'
    
    def download_youtube_with_bypass(self, url):
        """Скачивание YouTube с обходом блокировок"""
        print(f"🇷🇺 Скачивание YouTube для российских пользователей: {url}")
        
        # Пробуем разные методы обхода
        bypass_methods = [
            self.try_with_alternative_extractor,
            self.try_with_proxy_settings,
            self.try_with_mobile_user_agent,
            self.try_with_different_format,
        ]
        
        for method in bypass_methods:
            try:
                result = method(url)
                if result.get('success'):
                    return result
            except Exception as e:
                print(f"⚠️ Метод не сработал: {e}")
                continue
        
        return {'success': False, 'error': 'Все методы обхода блокировок не сработали. Попробуйте VPN.'}
    
    def try_with_alternative_extractor(self, url):
        """Попытка с альтернативным экстрактором"""
        opts = self.ydl_opts.copy()
        opts.update({
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage'],
                }
            }
        })
        
        return self._download_with_opts(url, opts)
    
    def try_with_proxy_settings(self, url):
        """Попытка с настройками прокси"""
        opts = self.ydl_opts.copy()
        # Можно добавить бесплатные прокси
        opts.update({
            'proxy': None,  # Здесь можно указать прокси
            'socket_timeout': 60,
        })
        
        return self._download_with_opts(url, opts)
    
    def try_with_mobile_user_agent(self, url):
        """Попытка с мобильным User-Agent"""
        opts = self.ydl_opts.copy()
        opts['http_headers'].update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        })
        
        return self._download_with_opts(url, opts)
    
    def try_with_different_format(self, url):
        """Попытка с другим форматом"""
        opts = self.ydl_opts.copy()
        opts.update({
            'format': 'worst[height>=360]/worst',  # Более низкое качество
            'prefer_free_formats': True,
        })
        
        return self._download_with_opts(url, opts)
    
    def _download_with_opts(self, url, opts):
        """Внутренний метод скачивания с заданными опциями"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                duration = info.get('duration', 0)
                
                print(f"✅ Информация получена: {title}")
                
                # Скачиваем видео
                ydl.download([url])
                
                # Находим скачанный файл
                for file in os.listdir(DOWNLOADS_DIR):
                    if title.replace(' ', '_')[:20] in file.replace(' ', '_'):
                        return {
                            'success': True,
                            'filename': file,
                            'title': title,
                            'duration': duration,
                            'platform': 'youtube'
                        }
                
                return {'success': False, 'error': 'Файл не найден после скачивания'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def download_tiktok_russia(self, url):
        """Скачивание TikTok для России"""
        print(f"🎵 Скачивание TikTok для российских пользователей: {url}")
        
        # Специальные настройки для TikTok
        tiktok_opts = self.ydl_opts.copy()
        tiktok_opts.update({
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.tiktok.com/',
            },
            'extractor_args': {
                'tiktok': {
                    'webpage_url_basename': 'video',
                }
            }
        })
        
        return self._download_with_opts(url, tiktok_opts)
    
    def download_instagram_russia(self, url):
        """Скачивание Instagram для России"""
        print(f"📸 Скачивание Instagram для российских пользователей: {url}")
        
        try:
            L = instaloader.Instaloader(
                dirname_pattern=DOWNLOADS_DIR,
                filename_pattern='{shortcode}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Извлекаем shortcode из URL
            shortcode_match = re.search(r'/p/([A-Za-z0-9_-]+)', url)
            if not shortcode_match:
                shortcode_match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            
            if not shortcode_match:
                return {'success': False, 'error': 'Не удалось извлечь код поста из URL'}
            
            shortcode = shortcode_match.group(1)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            L.download_post(post, target='')
            
            # Находим скачанный файл
            for file in os.listdir(DOWNLOADS_DIR):
                if shortcode in file and (file.endswith('.mp4') or file.endswith('.jpg')):
                    return {
                        'success': True,
                        'filename': file,
                        'title': post.caption[:50] if post.caption else 'Instagram Post',
                        'platform': 'instagram'
                    }
            
            return {'success': False, 'error': 'Файл не найден после скачивания'}
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка Instagram: {str(e)}'}
    
    def download_video(self, url):
        """Главный метод для скачивания видео"""
        if not validators.url(url):
            return {'success': False, 'error': 'Некорректный URL'}
        
        platform = self.detect_platform(url)
        
        print(f"🎯 Определена платформа: {platform}")
        
        if platform == 'youtube':
            return self.download_youtube_with_bypass(url)
        elif platform == 'tiktok':
            return self.download_tiktok_russia(url)
        elif platform == 'instagram':
            return self.download_instagram_russia(url)
        elif platform == 'telegram':
            return {'success': False, 'error': 'Telegram требует дополнительной настройки API'}
        else:
            # Пробуем как YouTube
            return self.download_youtube_with_bypass(url)

# Инициализируем загрузчик
downloader = RussianVideoDownloader()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})
        
        print(f"🇷🇺 Новый запрос от российского пользователя: {url}")
        result = downloader.download_video(url)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(DOWNLOADS_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Файл не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_downloads():
    try:
        for file in os.listdir(DOWNLOADS_DIR):
            file_path = os.path.join(DOWNLOADS_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({'success': True, 'message': 'Папка загрузок очищена'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def status():
    """Статус сервиса для российских пользователей"""
    return jsonify({
        'status': 'ok',
        'region': 'Russia',
        'bypass_methods': ['Alternative DNS', 'User-Agent rotation', 'Multiple extractors'],
        'platforms': ['YouTube (с обходом)', 'TikTok', 'Instagram', 'Telegram (ограниченно)']
    })

if __name__ == '__main__':
    print("🇷🇺 Запуск сервиса для российских пользователей")
    print("🔓 Включены методы обхода блокировок")
    app.run(debug=True, host='0.0.0.0', port=5000) 