#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, send_file, abort
import yt_dlp
import os
import re
import instaloader
from urllib.parse import urlparse
import requests
import time

DOWNLOADS_DIR = 'downloads'
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

app = Flask(__name__)

# Конфигурация proxy
PROXY_CONFIG = {
    'http_proxy': None,  # Например: 'http://proxy.example.com:8080'
    'socks_proxy': None,  # Например: 'socks5://proxy.example.com:1080'
    'enabled': False
}

# Список публичных proxy для автоматического использования
PUBLIC_PROXIES = [
    'http://103.152.112.145:80',
    'http://103.152.112.157:80',
    'http://181.78.18.219:999',
    'http://200.106.184.13:999',
    'http://20.111.54.16:80',
    'http://103.175.46.181:8080',
]



class ProxyDownloader:
    def __init__(self, custom_proxy=None):
        self.custom_proxy = custom_proxy
        self.current_proxy = None
        self.base_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]/best',
            'noplaylist': True,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'nocheckcertificate': True,
            'no_part': True,  # Отключаем .part файлы
            'overwrites': True,  # Перезаписываем файлы
        }
    
    def get_working_proxy(self):
        """Находит рабочий proxy из списка"""
        if self.custom_proxy:
            if self.test_proxy(self.custom_proxy):
                return self.custom_proxy
        
        for proxy in PUBLIC_PROXIES:
            if self.test_proxy(proxy):
                print(f"✅ Найден рабочий proxy: {proxy}")
                return proxy
        
        print("⚠️ Рабочий proxy не найден, используем прямое соединение")
        return None
    
    def test_proxy(self, proxy_url):
        """Тестирует proxy на работоспособность"""
        try:
            proxies = {'http': proxy_url, 'https': proxy_url}
            response = requests.get('http://httpbin.org/ip', 
                                  proxies=proxies, 
                                  timeout=10)
            if response.status_code == 200:
                return True
        except:
            pass
        return False
    
    def clean_url(self, url):
        """Очищает URL от лишних параметров"""
        parsed = urlparse(url)
        
        # Для TikTok удаляем browser tracking параметры
        if 'tiktok.com' in parsed.netloc:
            # Удаляем is_from_webapp, sender_device и другие tracking параметры
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            print(f"📝 Очищен TikTok URL: {clean_url}")
            return clean_url
        
        # Для YouTube удаляем utm и tracking параметры
        elif any(x in parsed.netloc for x in ['youtube.com', 'youtu.be']):
            if parsed.query:
                # Оставляем только v= для YouTube
                params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
                if 'v' in params:
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?v={params['v']}"
                else:
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                print(f"📝 Очищен YouTube URL: {clean_url}")
                return clean_url
        
        # Для Instagram - оставляем как есть
        return url
    
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
    
    def download_with_proxy(self, url, proxy_url=None):
        """Скачивание с использованием proxy"""
        opts = self.base_opts.copy()
        
        if proxy_url:
            opts['proxy'] = proxy_url
            print(f"🌐 Используется proxy: {proxy_url}")
        
        platform = self.detect_platform(url)
        
        if platform == 'tiktok':
            return self.download_tiktok_proxy(url, opts)
        elif platform == 'youtube':
            return self.download_youtube_proxy(url, opts)
        elif platform == 'instagram':
            return self.download_instagram_proxy(url, proxy_url)
        else:
            return {'success': False, 'error': f'Платформа {platform} не поддерживается'}
    
    def download_tiktok_proxy(self, url, opts):
        """TikTok с proxy"""
        tiktok_methods = [
            # Метод 1: Мобильное приложение
            {
                'http_headers': {
                    'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
                    'X-Requested-With': 'com.zhiliaoapp.musically',
                },
                'extractor_args': {
                    'tiktok': {
                        'api_hostname': 'api.tiktokv.com',
                    }
                }
            },
            # Метод 2: Web версия
            {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                    'Referer': 'https://www.tiktok.com/',
                }
            }
        ]
        
        for i, method_opts in enumerate(tiktok_methods, 1):
            print(f"🔄 TikTok метод {i}")
            try:
                current_opts = opts.copy()
                current_opts.update(method_opts)
                
                with yt_dlp.YoutubeDL(current_opts) as ydl:
                    info = ydl.extract_info(url)
                    filename = ydl.prepare_filename(info)
                    
                    if os.path.exists(filename):
                        return {
                            'success': True,
                            'filename': os.path.basename(filename),
                            'title': info.get('title', 'TikTok Video'),
                            'platform': 'tiktok',
                            'proxy_used': opts.get('proxy', 'Нет')
                        }
            except Exception as e:
                print(f"❌ Метод {i} не сработал: {e}")
        
        return {
            'success': False, 
            'error': 'TikTok заблокирован. Нужен VPN или proxy.',
            'suggestions': [
                '🌐 Настройте proxy в приложении',
                '🔧 Попробуйте другой proxy сервер',
                '📱 Используйте мобильный интернет + VPN'
            ]
        }
    
    def download_youtube_proxy(self, url, opts):
        """YouTube с proxy"""
        youtube_methods = [
            # Android клиент
            {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['webpage', 'configs'],
                    }
                }
            },
            # iOS клиент  
            {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'com.google.ios.youtube/17.33.2 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
                }
            }
        ]
        
        for i, method_opts in enumerate(youtube_methods, 1):
            print(f"🔄 YouTube метод {i}")
            try:
                current_opts = opts.copy()
                current_opts.update(method_opts)
                
                with yt_dlp.YoutubeDL(current_opts) as ydl:
                    info = ydl.extract_info(url)
                    filename = ydl.prepare_filename(info)
                    
                    if os.path.exists(filename):
                        return {
                            'success': True,
                            'filename': os.path.basename(filename),
                            'title': info.get('title', 'YouTube Video'),
                            'platform': 'youtube',
                            'proxy_used': opts.get('proxy', 'Нет')
                        }
            except Exception as e:
                print(f"❌ Метод {i} не сработал: {e}")
        
        return {'success': False, 'error': 'YouTube недоступен. Попробуйте proxy.'}
    
    def download_instagram_proxy(self, url, proxy_url=None):
        """Instagram с proxy"""
        try:
            # Настройка instaloader с proxy
            session = requests.Session()
            if proxy_url:
                session.proxies = {'http': proxy_url, 'https': proxy_url}
            
            L = instaloader.Instaloader(
                dirname_pattern=DOWNLOADS_DIR,
                filename_pattern='{shortcode}',
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                request_timeout=30,
                max_connection_attempts=3,
                session=session
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
                        'platform': 'instagram',
                        'proxy_used': proxy_url or 'Нет'
                    }
            
            return {'success': False, 'error': 'Файл не найден после скачивания'}
            
        except Exception as e:
            return {'success': False, 'error': f'Ошибка Instagram: {str(e)}'}
    
    def download_video(self, url):
        """Основной метод скачивания с автоматическим выбором proxy"""
        print(f"🎬 Начинаем скачивание: {url}")
        
        # Очищаем URL от лишних параметров
        clean_url = self.clean_url(url)
        if clean_url != url:
            print(f"🔄 Используем очищенный URL: {clean_url}")
            url = clean_url
        
        # Пробуем без proxy
        try:
            result = self.download_with_proxy(url)
            if result.get('success'):
                return result
        except Exception as e:
            print(f"⚠️ Прямое соединение не работает: {e}")
        
        # Ищем рабочий proxy
        working_proxy = self.get_working_proxy()
        if working_proxy:
            try:
                result = self.download_with_proxy(url, working_proxy)
                if result.get('success'):
                    return result
            except Exception as e:
                print(f"⚠️ Proxy не помог: {e}")
        
        return {
            'success': False, 
            'error': 'Не удалось скачать видео. Попробуйте настроить VPN.',
            'suggestions': [
                '🌐 Настройте VPN соединение',
                '🔧 Попробуйте другое время',
                '📱 Используйте мобильный интернет'
            ]
        }

# Создаем глобальный экземпляр
downloader = ProxyDownloader()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url', '').strip()
        custom_proxy = data.get('proxy', '').strip()  # Пользователь может указать свой proxy
        
        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})
        
        # Используем custom proxy если указан
        if custom_proxy:
            downloader.custom_proxy = custom_proxy
        
        result = downloader.download_video(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'})

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            abort(404)
    except Exception as e:
        abort(500)

@app.route('/cleanup', methods=['POST'])
def cleanup_downloads():
    try:
        files_removed = 0
        for filename in os.listdir(DOWNLOADS_DIR):
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
                files_removed += 1
        
        return jsonify({
            'success': True, 
            'message': f'Удалено {files_removed} файлов'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def status():
    return jsonify({
        'status': 'working',
        'proxy_support': True,
        'available_proxies': len(PUBLIC_PROXIES),
        'platforms': {
            'tiktok': 'Поддержка с proxy',
            'youtube': 'Поддержка с proxy',
            'instagram': 'Поддержка с proxy',
            'telegram': 'Базовая поддержка'
        }
    })

@app.route('/test_proxy', methods=['POST'])
def test_proxy():
    """Тестирование пользовательского proxy"""
    try:
        data = request.json
        proxy_url = data.get('proxy', '').strip()
        
        if not proxy_url:
            return jsonify({'success': False, 'error': 'Proxy URL не указан'})
        
        test_downloader = ProxyDownloader()
        is_working = test_downloader.test_proxy(proxy_url)
        
        return jsonify({
            'success': True,
            'working': is_working,
            'proxy': proxy_url,
            'message': 'Proxy работает!' if is_working else 'Proxy не отвечает'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка тестирования: {str(e)}'})



if __name__ == '__main__':
    print("🚀 Запуск сервиса скачивания видео")
    print("🌐 Поддержка автоматического поиска рабочих proxy")
    print("🔧 Можно указать свой proxy в настройках")
    print("📱 Поддержка TikTok, YouTube, Instagram, Telegram")
    print("📊 Доступно на: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True) 