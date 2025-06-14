import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Основные настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'videodl-secret-key-2024'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Настройки сервера
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # Папка для загрузок
    DOWNLOADS_DIR = os.environ.get('DOWNLOADS_DIR') or 'downloads'
    
    # Максимальный размер файла (по умолчанию 500MB)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 500 * 1024 * 1024)
    
    # Настройки качества видео
    VIDEO_QUALITY = os.environ.get('VIDEO_QUALITY') or 'best[height<=720]/best'
    
    # Настройки yt-dlp
    YDL_OPTS = {
        'format': VIDEO_QUALITY,
        'noplaylist': True,
        'extractaudio': False,
        'audioformat': 'mp3',
        'embed_thumbnail': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
    }
    
    # Telegram API (опционально)
    TELEGRAM_API_ID = os.environ.get('TELEGRAM_API_ID')
    TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    # Instagram настройки (опционально)
    INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME')
    INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD')
    
    # Поддерживаемые платформы
    SUPPORTED_PLATFORMS = {
        'youtube': {
            'domains': ['youtube.com', 'youtu.be', 'm.youtube.com', 'music.youtube.com'],
            'name': 'YouTube',
            'emoji': '🎬'
        },
        'tiktok': {
            'domains': ['tiktok.com', 'vm.tiktok.com', 'm.tiktok.com', 'vt.tiktok.com'],
            'name': 'TikTok',
            'emoji': '🎵'
        },
        'instagram': {
            'domains': ['instagram.com', 'm.instagram.com', 'www.instagram.com'],
            'name': 'Instagram',
            'emoji': '📸'
        },
        'telegram': {
            'domains': ['t.me', 'telegram.me', 'telegram.org'],
            'name': 'Telegram',
            'emoji': '💬'
        }
    }
    
    # Настройки безопасности
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'm4a', 'jpg', 'png'}
    MAX_FILENAME_LENGTH = 255
    
    @staticmethod
    def get_platform_info(platform_name):
        """Получить информацию о платформе"""
        return Config.SUPPORTED_PLATFORMS.get(platform_name, {})
    
    @staticmethod
    def is_platform_supported(domain):
        """Проверить, поддерживается ли платформа"""
        domain = domain.lower()
        for platform, info in Config.SUPPORTED_PLATFORMS.items():
            if any(d in domain for d in info['domains']):
                return platform
        return None 