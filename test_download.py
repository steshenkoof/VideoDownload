#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации API скачивания видео
"""

import requests
import json
import time

# Настройки
BASE_URL = "http://127.0.0.1:5000"
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (классика)
    "https://www.tiktok.com/@example/video/123456789",  # TikTok (пример)
    "https://www.instagram.com/p/example/",  # Instagram (пример)
]

def test_video_info(url):
    """Тестирует получение информации о видео"""
    print(f"\n🔍 Получаем информацию о видео: {url}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/info",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Платформа: {data.get('platform', 'Unknown')}")
                print(f"📺 Название: {data.get('title', 'Unknown')}")
                print(f"👤 Автор: {data.get('uploader', 'Unknown')}")
                print(f"⏱️ Длительность: {data.get('duration', 0)} сек")
                print(f"👀 Просмотры: {data.get('view_count', 0)}")
                return True
            else:
                print(f"❌ Ошибка: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def test_video_download(url):
    """Тестирует скачивание видео"""
    print(f"\n⬇️  Скачиваем видео: {url}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/download",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Видео скачано!")
                print(f"📁 Файл: {data.get('filename', 'Unknown')}")
                print(f"📺 Название: {data.get('title', 'Unknown')}")
                print(f"🎬 Платформа: {data.get('platform', 'Unknown')}")
                
                # Пробуем получить список файлов
                files_response = requests.get(f"{BASE_URL}/files")
                if files_response.status_code == 200:
                    files_data = files_response.json()
                    if files_data.get('success'):
                        print(f"📊 Всего файлов в системе: {len(files_data.get('files', []))}")
                
                return True
            else:
                print(f"❌ Ошибка скачивания: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def test_stats():
    """Получает статистику сервиса"""
    print(f"\n📊 Получаем статистику сервиса...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Статистика:")
                print(f"📁 Всего файлов: {data.get('total_files', 0)}")
                print(f"💾 Общий размер: {data.get('total_size_mb', 0)} MB")
                print(f"📱 Поддерживаемые платформы: {', '.join(data.get('supported_platforms', []))}")
                print(f"⚙️  Максимальный размер файла: {data.get('max_file_size_mb', 0)} MB")
                return True
            else:
                print(f"❌ Ошибка: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def interactive_test():
    """Интерактивный тест с пользовательским вводом"""
    print("\n🎯 Интерактивный тест скачивания видео")
    print("Введите ссылку на видео (или 'exit' для выхода):")
    
    while True:
        url = input("\n🔗 URL: ").strip()
        
        if url.lower() in ['exit', 'quit', 'выход']:
            break
            
        if not url:
            print("❌ Введите корректную ссылку!")
            continue
            
        # Сначала получаем информацию
        if test_video_info(url):
            # Спрашиваем, скачивать ли
            choice = input("\n❓ Скачать это видео? (y/n): ").strip().lower()
            if choice in ['y', 'yes', 'да', 'д']:
                test_video_download(url)
        
        print("\n" + "="*50)

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование сервиса VideoDL")
    print("="*50)
    
    # Проверяем доступность сервиса
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ Сервис недоступен! Код ответа: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Не удается подключиться к серверу: {e}")
        print("Убедитесь, что сервер запущен: python app.py")
        return
    
    print("✅ Сервис доступен!")
    
    # Получаем статистику
    test_stats()
    
    # Тестируем с примерами
    print(f"\n🧪 Тестируем получение информации о видео...")
    for url in TEST_URLS[:1]:  # Только первый для демонстрации
        test_video_info(url)
        time.sleep(1)
    
    # Интерактивный режим
    try:
        interactive_test()
    except KeyboardInterrupt:
        print("\n\n👋 Тестирование завершено!")

if __name__ == "__main__":
    main() 