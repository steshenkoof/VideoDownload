#!/usr/bin/env python3
"""
Простой тест для основного API скачивания
"""

import requests
import json

def test_download(url):
    """Тестирует скачивание видео через основной API"""
    print(f"🔗 Тестируем скачивание: {url}")
    print("⏳ Отправляем запрос...")
    
    try:
        # Отправляем POST запрос на /download
        response = requests.post(
            "http://127.0.0.1:5000/download",
            json={"url": url},
            headers={"Content-Type": "application/json"},
            timeout=60  # Увеличиваем таймаут для скачивания
        )
        
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Ответ сервера:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print(f"\n✅ Успешно скачано!")
                print(f"📁 Файл: {data.get('filename', 'Unknown')}")
                print(f"📺 Название: {data.get('title', 'Unknown')}")
                print(f"🎬 Платформа: {data.get('platform', 'Unknown')}")
                
                if 'duration' in data:
                    print(f"⏱️ Длительность: {data['duration']} сек")
                if 'uploader' in data:
                    print(f"👤 Автор: {data['uploader']}")
                    
                # Показываем ссылку для скачивания
                filename = data.get('filename')
                if filename:
                    download_url = f"http://127.0.0.1:5000/download_file/{filename}"
                    print(f"🔗 Ссылка для скачивания: {download_url}")
                
                return True
            else:
                print(f"❌ Ошибка: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Превышено время ожидания (60 сек)")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("🚀 Простой тест скачивания видео")
    print("="*50)
    
    # Проверяем доступность сервера
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен!")
        else:
            print(f"⚠️ Сервер отвечает с кодом: {response.status_code}")
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        return
    
    # TikTok ссылка от пользователя
    tiktok_url = "https://www.tiktok.com/@b2zfamily/video/7513864181188365591?is_from_webapp=1&sender_device=pc"
    
    print(f"\n🎵 Тестируем TikTok видео...")
    test_download(tiktok_url)
    
    print(f"\n" + "="*50)
    print("Также можете открыть браузер и перейти по адресу:")
    print("🌐 http://127.0.0.1:5000")
    print("Там есть красивый веб-интерфейс для скачивания!")

if __name__ == "__main__":
    main() 