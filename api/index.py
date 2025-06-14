#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
import tempfile
import json
from urllib.parse import urlparse

app = Flask(__name__, template_folder='../templates')

# Для Vercel используем временные файлы
TEMP_DIR = tempfile.gettempdir()

def detect_platform(url):
    """Определяет платформу по URL"""
    domain = urlparse(url).netloc.lower()
    
    if any(x in domain for x in ['youtube.com', 'youtu.be', 'm.youtube.com']):
        return 'youtube'
    elif any(x in domain for x in ['tiktok.com', 'vm.tiktok.com', 'm.tiktok.com']):
        return 'tiktok'
    elif any(x in domain for x in ['instagram.com', 'm.instagram.com']):
        return 'instagram'
    else:
        return 'unknown'

def download_video_info(url):
    """Получает информацию о видео без скачивания"""
    try:
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 30,
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'success': True,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'platform': detect_platform(url),
                'formats': [
                    {
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'quality': f.get('height', 0),
                        'filesize': f.get('filesize', 0),
                        'url': f.get('url', '')
                    }
                    for f in info.get('formats', [])[:5]  # Только первые 5 форматов
                ]
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    return render_template('index_vercel.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """API для получения информации о видео"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})
        
        result = download_video_info(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка обработки: {str(e)}'
        })

@app.route('/api/download', methods=['POST'])
def download_video():
    """Упрощенное API для скачивания (только получение прямой ссылки)"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'URL не указан'})
        
        # Из-за ограничений Vercel, возвращаем только прямую ссылку
        opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720]/best',
            'socket_timeout': 15,  # Короткий таймаут для Vercel
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Находим лучший формат
            formats = info.get('formats', [])
            if formats:
                best_format = formats[0]
                direct_url = best_format.get('url', '')
                
                return jsonify({
                    'success': True,
                    'title': info.get('title', 'Video'),
                    'direct_url': direct_url,
                    'platform': detect_platform(url),
                    'note': 'Из-за ограничений Vercel, предоставляется прямая ссылка для скачивания'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Не удалось получить ссылку для скачивания'
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка: {str(e)}',
            'suggestion': 'Попробуйте использовать VPN или другой сервер'
        })

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'platform': 'vercel',
        'limitations': [
            'Время выполнения ограничено 10 секундами',
            'Размер ответа ограничен 4.5MB',
            'Нет постоянного хранилища файлов',
            'Предоставляются только прямые ссылки'
        ]
    })

# Для локального тестирования
if __name__ == '__main__':
    app.run(debug=True)

# Экспорт для Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None) 