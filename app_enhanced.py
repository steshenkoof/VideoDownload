import os
import re
import json
import tempfile
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import validators
from urllib.parse import urlparse
import instaloader
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Создаем папку для загрузок
if not os.path.exists(Config.DOWNLOADS_DIR):
    os.makedirs(Config.DOWNLOADS_DIR)
    logger.info(f"Создана папка для загрузок: {Config.DOWNLOADS_DIR}")

class VideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'outtmpl': os.path.join(Config.DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            **Config.YDL_OPTS
        }
        logger.info("Инициализирован VideoDownloader")
    
    def detect_platform(self, url):
        """Определяет платформу по URL"""
        try:
            domain = urlparse(url).netloc.lower()
            platform = Config.is_platform_supported(domain)
            logger.info(f"Обнаружена платформа: {platform} для URL: {url}")
            return platform or 'unknown'
        except Exception as e:
            logger.error(f"Ошибка определения платформы для {url}: {e}")
            return 'unknown'
    
    def sanitize_filename(self, filename):
        """Очистка имени файла от недопустимых символов"""
        # Удаляем недопустимые символы
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Ограничиваем длину
        if len(filename) > Config.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(filename)
            filename = name[:Config.MAX_FILENAME_LENGTH-len(ext)] + ext
        return filename
    
    def download_youtube_tiktok(self, url):
        """Скачивает видео с YouTube или TikTok через yt-dlp"""
        try:
            logger.info(f"Начинаем скачивание с YouTube/TikTok: {url}")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                view_count = info.get('view_count', 0)
                
                logger.info(f"Информация о видео: {title} ({duration}s)")
                
                # Скачиваем видео
                ydl.download([url])
                
                # Находим скачанный файл
                expected_filename = self.sanitize_filename(f"{title}.mp4")
                for file in os.listdir(Config.DOWNLOADS_DIR):
                    if title.replace(' ', '_')[:30] in file.replace(' ', '_'):
                        logger.info(f"Файл успешно скачан: {file}")
                        return {
                            'success': True,
                            'filename': file,
                            'title': title,
                            'duration': duration,
                            'uploader': uploader,
                            'view_count': view_count,
                            'platform': self.detect_platform(url)
                        }
                
                logger.error("Файл не найден после скачивания")
                return {'success': False, 'error': 'Файл не найден после скачивания'}
                
        except yt_dlp.DownloadError as e:
            logger.error(f"Ошибка yt-dlp при скачивании {url}: {e}")
            return {'success': False, 'error': f'Ошибка скачивания: {str(e)}'}
        except Exception as e:
            logger.error(f"Общая ошибка при скачивании {url}: {e}")
            return {'success': False, 'error': f'Неожиданная ошибка: {str(e)}'}
    
    def download_instagram(self, url):
        """Скачивает видео с Instagram через instaloader"""
        try:
            logger.info(f"Начинаем скачивание с Instagram: {url}")
            
            L = instaloader.Instaloader(
                dirname_pattern=Config.DOWNLOADS_DIR,
                filename_pattern='{shortcode}',
                download_videos=True,
                download_pictures=True,
                save_metadata=False,
                compress_json=False
            )
            
            # Извлекаем shortcode из URL
            shortcode_match = re.search(r'/p/([A-Za-z0-9_-]+)', url)
            if not shortcode_match:
                shortcode_match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            
            if not shortcode_match:
                logger.error(f"Не удалось извлечь shortcode из URL: {url}")
                return {'success': False, 'error': 'Не удалось извлечь код поста из URL'}
            
            shortcode = shortcode_match.group(1)
            logger.info(f"Извлечен shortcode: {shortcode}")
            
            # Получаем пост
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Скачиваем пост
            L.download_post(post, target='')
            
            # Находим скачанный файл
            for file in os.listdir(Config.DOWNLOADS_DIR):
                if shortcode in file and any(file.endswith(ext) for ext in ['.mp4', '.jpg', '.png']):
                    logger.info(f"Instagram файл успешно скачан: {file}")
                    return {
                        'success': True,
                        'filename': file,
                        'title': post.caption[:100] if post.caption else f'Instagram Post {shortcode}',
                        'platform': 'instagram',
                        'uploader': post.owner_username,
                        'likes': post.likes,
                        'date': post.date_local.isoformat()
                    }
            
            logger.error("Instagram файл не найден после скачивания")
            return {'success': False, 'error': 'Файл не найден после скачивания'}
            
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Instagram профиль не существует: {url}")
            return {'success': False, 'error': 'Профиль или пост не существует'}
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            logger.error(f"Приватный Instagram профиль: {url}")
            return {'success': False, 'error': 'Профиль приватный. Требуется авторизация'}
        except Exception as e:
            logger.error(f"Ошибка при скачивании с Instagram {url}: {e}")
            return {'success': False, 'error': f'Ошибка Instagram: {str(e)}'}
    
    def download_telegram(self, url):
        """Обработка Telegram ссылок"""
        logger.info(f"Попытка скачивания с Telegram: {url}")
        
        if not all([Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH]):
            logger.warning("Telegram API не настроен")
            return {
                'success': False, 
                'error': 'Скачивание с Telegram требует настройки API. Добавьте TELEGRAM_API_ID и TELEGRAM_API_HASH в переменные окружения.'
            }
        
        # Здесь можно добавить реализацию с pyrogram или telethon
        return {
            'success': False, 
            'error': 'Функция скачивания с Telegram в разработке. Используйте Telegram Desktop.'
        }
    
    def get_video_info(self, url):
        """Получает информацию о видео без скачивания"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
                }
        except Exception as e:
            logger.error(f"Ошибка получения информации о видео: {e}")
            return None
    
    def download_video(self, url):
        """Главный метод для скачивания видео"""
        logger.info(f"Запрос на скачивание: {url}")
        
        # Валидация URL
        if not validators.url(url):
            logger.error(f"Некорректный URL: {url}")
            return {'success': False, 'error': 'Некорректный URL'}
        
        platform = self.detect_platform(url)
        
        try:
            if platform in ['youtube', 'tiktok']:
                return self.download_youtube_tiktok(url)
            elif platform == 'instagram':
                return self.download_instagram(url)
            elif platform == 'telegram':
                return self.download_telegram(url)
            else:
                # Пробуем через yt-dlp для неизвестных платформ
                logger.info(f"Неизвестная платформа, пробуем yt-dlp: {platform}")
                return self.download_youtube_tiktok(url)
        except Exception as e:
            logger.error(f"Критическая ошибка при скачивании {url}: {e}")
            return {'success': False, 'error': f'Критическая ошибка: {str(e)}'}

# Инициализируем загрузчик
downloader = VideoDownloader()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/info', methods=['POST'])
def get_video_info():
    """Получить информацию о видео без скачивания"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})
        
        info = downloader.get_video_info(url)
        if info:
            info['success'] = True
            info['platform'] = downloader.detect_platform(url)
            return jsonify(info)
        else:
            return jsonify({'success': False, 'error': 'Не удалось получить информацию о видео'})
    
    except Exception as e:
        logger.error(f"Ошибка получения информации: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    """Скачивание видео"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})
        
        logger.info(f"Новый запрос на скачивание: {url}")
        result = downloader.download_video(url)
        
        if result['success']:
            logger.info(f"Успешно скачано: {result.get('filename', 'unknown')}")
        else:
            logger.error(f"Ошибка скачивания: {result.get('error', 'unknown')}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Критическая ошибка в /download: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_file/<filename>')
def download_file(filename):
    """Скачивание файла с сервера"""
    try:
        # Безопасная проверка имени файла
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(Config.DOWNLOADS_DIR, safe_filename)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            logger.info(f"Отправка файла пользователю: {safe_filename}")
            return send_file(file_path, as_attachment=True, download_name=safe_filename)
        else:
            logger.error(f"Файл не найден: {safe_filename}")
            return jsonify({'error': 'Файл не найден'}), 404
    except Exception as e:
        logger.error(f"Ошибка отправки файла {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    """Список загруженных файлов"""
    try:
        files = []
        for filename in os.listdir(Config.DOWNLOADS_DIR):
            file_path = os.path.join(Config.DOWNLOADS_DIR, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        logger.error(f"Ошибка получения списка файлов: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/cleanup', methods=['POST'])
def cleanup_downloads():
    """Очистка папки загрузок"""
    try:
        deleted_count = 0
        for filename in os.listdir(Config.DOWNLOADS_DIR):
            file_path = os.path.join(Config.DOWNLOADS_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
        
        logger.info(f"Удалено файлов: {deleted_count}")
        return jsonify({'success': True, 'message': f'Удалено файлов: {deleted_count}'})
    except Exception as e:
        logger.error(f"Ошибка очистки: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Статистика сервиса"""
    try:
        total_files = len([f for f in os.listdir(Config.DOWNLOADS_DIR) 
                          if os.path.isfile(os.path.join(Config.DOWNLOADS_DIR, f))])
        
        total_size = sum(os.path.getsize(os.path.join(Config.DOWNLOADS_DIR, f)) 
                        for f in os.listdir(Config.DOWNLOADS_DIR) 
                        if os.path.isfile(os.path.join(Config.DOWNLOADS_DIR, f)))
        
        stats = {
            'success': True,
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'supported_platforms': list(Config.SUPPORTED_PLATFORMS.keys()),
            'max_file_size_mb': round(Config.MAX_CONTENT_LENGTH / (1024 * 1024), 2)
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Страница не найдена'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Внутренняя ошибка сервера: {error}")
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

if __name__ == '__main__':
    logger.info(f"Запуск сервера на {Config.HOST}:{Config.PORT}")
    logger.info(f"Папка загрузок: {Config.DOWNLOADS_DIR}")
    logger.info(f"Поддерживаемые платформы: {list(Config.SUPPORTED_PLATFORMS.keys())}")
    
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT) 