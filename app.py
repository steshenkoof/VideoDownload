import os
import re
import json
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import validators
from urllib.parse import urlparse
import instaloader

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Создаем папку для загрузок
DOWNLOADS_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

class VideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]/best',  # Оптимальное качество
            'noplaylist': True,
        }
    
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
    
    def download_youtube_tiktok(self, url):
        """Скачивает видео с YouTube или TikTok через yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                duration = info.get('duration', 0)
                
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
                            'platform': self.detect_platform(url)
                        }
                
                return {'success': False, 'error': 'Файл не найден после скачивания'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def download_instagram(self, url):
        """Скачивает видео с Instagram через instaloader"""
        try:
            L = instaloader.Instaloader(
                dirname_pattern=DOWNLOADS_DIR,
                filename_pattern='{shortcode}'
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
            return {'success': False, 'error': str(e)}
    
    def download_telegram(self, url):
        """Обработка Telegram ссылок (требует дополнительной настройки API)"""
        return {
            'success': False, 
            'error': 'Скачивание с Telegram требует настройки API. Пожалуйста, используйте Telegram Desktop для скачивания.'
        }
    
    def download_video(self, url):
        """Главный метод для скачивания видео"""
        if not validators.url(url):
            return {'success': False, 'error': 'Некорректный URL'}
        
        platform = self.detect_platform(url)
        
        if platform in ['youtube', 'tiktok']:
            return self.download_youtube_tiktok(url)
        elif platform == 'instagram':
            return self.download_instagram(url)
        elif platform == 'telegram':
            return self.download_telegram(url)
        else:
            # Пробуем через yt-dlp для других платформ
            return self.download_youtube_tiktok(url)

downloader = VideoDownloader()

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
    """Очистка папки загрузок"""
    try:
        for file in os.listdir(DOWNLOADS_DIR):
            file_path = os.path.join(DOWNLOADS_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({'success': True, 'message': 'Папка загрузок очищена'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 