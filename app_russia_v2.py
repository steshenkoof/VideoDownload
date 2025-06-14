import os
import re
import json
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import validators
from urllib.parse import urlparse
import instaloader

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

DOWNLOADS_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

class AdvancedRussianDownloader:
    def __init__(self):
        # Базовые настройки с продвинутыми методами обхода
        self.base_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]/best',
            'noplaylist': True,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'nocheckcertificate': True,
        }
        
        # Список прокси для обхода (можно добавить реальные)
        self.proxy_list = [
            None,  # Без прокси
            # 'http://proxy1.example.com:8080',
            # 'socks5://proxy2.example.com:1080',
        ]
        
        # Различные User-Agent для обхода
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
        ]
    
    def detect_platform(self, url):
        """Определяет платформу по URL"""
        domain = urlparse(url).netloc.lower()
        
        if any(x in domain for x in ['youtube.com', 'youtu.be', 'm.youtube.com']):
            return 'youtube'
        elif any(x in domain for x in ['tiktok.com', 'vm.tiktok.com', 'm.tiktok.com', 'vt.tiktok.com']):
            return 'tiktok'
        elif any(x in domain for x in ['instagram.com', 'm.instagram.com']):
            return 'instagram'
        elif any(x in domain for x in ['t.me', 'telegram.me']):
            return 'telegram'
        else:
            return 'unknown'
    
    def download_tiktok_advanced(self, url):
        """Продвинутое скачивание TikTok с множественными методами обхода"""
        print(f"🎵 Продвинутое скачивание TikTok: {url}")
        
        # Методы обхода для TikTok
        methods = [
            self.tiktok_method_mobile,
            self.tiktok_method_api,
            self.tiktok_method_web,
            self.tiktok_method_alternative,
        ]
        
        for i, method in enumerate(methods, 1):
            print(f"🔄 Попытка {i}: {method.__name__}")
            try:
                result = method(url)
                if result.get('success'):
                    print(f"✅ Успех с методом {i}!")
                    return result
                else:
                    print(f"⚠️ Метод {i} не сработал: {result.get('error', 'Unknown')}")
            except Exception as e:
                print(f"❌ Ошибка в методе {i}: {e}")
        
        return {
            'success': False, 
            'error': 'TikTok заблокирован. Попробуйте VPN или другую сеть.',
            'suggestions': [
                '🌐 Включите VPN (ProtonVPN, Windscribe)',
                '📱 Попробуйте мобильный интернет',
                '🔧 Смените DNS на 1.1.1.1',
                '⏰ Попробуйте позже'
            ]
        }
    
    def tiktok_method_mobile(self, url):
        """Метод 1: Мобильный User-Agent"""
        opts = self.base_opts.copy()
        opts.update({
            'http_headers': {
                'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
                'X-Requested-With': 'com.zhiliaoapp.musically',
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api.tiktokv.com',
                }
            }
        })
        return self._try_download(url, opts, 'mobile')
    
    def tiktok_method_api(self, url):
        """Метод 2: Альтернативное API"""
        opts = self.base_opts.copy()
        opts.update({
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                'Referer': 'https://www.tiktok.com/',
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api.tiktokv.com',
                    'app_version': '26.2.0',
                }
            }
        })
        return self._try_download(url, opts, 'api')
    
    def tiktok_method_web(self, url):
        """Метод 3: Веб-версия"""
        opts = self.base_opts.copy()
        opts.update({
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.tiktok.com/',
            }
        })
        return self._try_download(url, opts, 'web')
    
    def tiktok_method_alternative(self, url):
        """Метод 4: Альтернативные настройки"""
        opts = self.base_opts.copy()
        opts.update({
            'format': 'worst/best',  # Более низкое качество
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            },
            'sleep_interval': 1,
            'max_sleep_interval': 3,
        })
        return self._try_download(url, opts, 'alternative')
    
    def download_youtube_russia(self, url):
        """Скачивание YouTube для России"""
        print(f"🎬 Скачивание YouTube: {url}")
        
        methods = [
            self.youtube_method_android,
            self.youtube_method_ios,
            self.youtube_method_web,
        ]
        
        for method in methods:
            try:
                result = method(url)
                if result.get('success'):
                    return result
            except Exception as e:
                print(f"⚠️ YouTube метод не сработал: {e}")
        
        return {'success': False, 'error': 'YouTube недоступен. Попробуйте VPN.'}
    
    def youtube_method_android(self, url):
        """YouTube через Android клиент"""
        opts = self.base_opts.copy()
        opts.update({
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage', 'configs'],
                }
            }
        })
        return self._try_download(url, opts, 'youtube-android')
    
    def youtube_method_ios(self, url):
        """YouTube через iOS клиент"""
        opts = self.base_opts.copy()
        opts.update({
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/17.33.2 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
            }
        })
        return self._try_download(url, opts, 'youtube-ios')
    
    def youtube_method_web(self, url):
        """YouTube через веб-клиент"""
        opts = self.base_opts.copy()
        opts.update({
            'extractor_args': {
                'youtube': {
                    'player_client': ['web'],
                }
            }
        })
        return self._try_download(url, opts, 'youtube-web')
    
    def download_instagram_russia(self, url):
        """Скачивание Instagram для России"""
        print(f"📸 Скачивание Instagram: {url}")
        
        try:
            L = instaloader.Instaloader(
                dirname_pattern=DOWNLOADS_DIR,
                filename_pattern='{shortcode}',
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                request_timeout=30,
                max_connection_attempts=3
            )
            
            shortcode_match = re.search(r'/p/([A-Za-z0-9_-]+)', url)
            if not shortcode_match:
                shortcode_match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            
            if not shortcode_match:
                return {'success': False, 'error': 'Не удалось извлечь код поста из URL'}
            
            shortcode = shortcode_match.group(1)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            L.download_post(post, target='')
            
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
            return {'success': False, 'error': f'Instagram ошибка: {str(e)}'}
    
    def _try_download(self, url, opts, method_name):
        """Внутренний метод для попытки скачивания"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                duration = info.get('duration', 0)
                
                ydl.download([url])
                
                for file in os.listdir(DOWNLOADS_DIR):
                    if title.replace(' ', '_')[:20] in file.replace(' ', '_'):
                        return {
                            'success': True,
                            'filename': file,
                            'title': title,
                            'duration': duration,
                            'platform': self.detect_platform(url),
                            'method': method_name
                        }
                
                return {'success': False, 'error': 'Файл не найден после скачивания'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def download_video(self, url):
        """Главный метод скачивания"""
        if not validators.url(url):
            return {'success': False, 'error': 'Некорректный URL'}
        
        platform = self.detect_platform(url)
        print(f"🎯 Платформа: {platform}")
        
        if platform == 'tiktok':
            return self.download_tiktok_advanced(url)
        elif platform == 'youtube':
            return self.download_youtube_russia(url)
        elif platform == 'instagram':
            return self.download_instagram_russia(url)
        elif platform == 'telegram':
            return {'success': False, 'error': 'Telegram требует настройки API'}
        else:
            return self.download_youtube_russia(url)  # Пробуем как YouTube

# Инициализация
downloader = AdvancedRussianDownloader()

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
        
        print(f"🇷🇺 Продвинутый российский загрузчик: {url}")
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
        count = 0
        for file in os.listdir(DOWNLOADS_DIR):
            file_path = os.path.join(DOWNLOADS_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        return jsonify({'success': True, 'message': f'Удалено файлов: {count}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def status():
    return jsonify({
        'status': 'advanced',
        'region': 'Russia',
        'version': '2.0',
        'bypass_methods': [
            'Multiple User-Agents',
            'Alternative APIs', 
            'Mobile emulation',
            'Proxy rotation support',
            'Multiple retry strategies'
        ],
        'platforms': {
            'tiktok': '4 методы обхода',
            'youtube': '3 метода обхода', 
            'instagram': 'Optimized for Russia',
            'telegram': 'Требует API'
        }
    })

if __name__ == '__main__':
    print("🇷🇺 Запуск ПРОДВИНУТОЙ российской версии v2.0")
    print("🔓 Включены множественные методы обхода блокировок")
    print("📊 Поддержка: TikTok (4 метода), YouTube (3 метода), Instagram")
    app.run(debug=True, host='0.0.0.0', port=5001)  # Другой порт 