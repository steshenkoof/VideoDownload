#!/usr/bin/env python3
"""
Тест для российской версии с обходом блокировок
"""

import requests
import json

def test_russian_youtube():
    """Тестирует YouTube с обходом блокировок"""
    print("🇷🇺 Тестируем YouTube с российскими настройками обхода")
    
    # Используем менее известное видео для тестирования
    test_urls = [
        "https://www.youtube.com/watch?v=BaW_jenozKc",  # Короткое видео
        "https://youtu.be/BaW_jenozKc",  # Короткая ссылка
    ]
    
    for url in test_urls:
        print(f"\n🔗 Тестируем: {url}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:5000/download",
                json={"url": url},
                headers={"Content-Type": "application/json"},
                timeout=90
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ УСПЕХ! Скачано: {data.get('filename')}")
                    print(f"📺 Название: {data.get('title')}")
                    return True
                else:
                    print(f"❌ Ошибка: {data.get('error')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")
    
    return False

def test_status():
    """Проверяем статус российского сервиса"""
    try:
        response = requests.get("http://127.0.0.1:5000/status")
        if response.status_code == 200:
            data = response.json()
            print("🇷🇺 Статус российского сервиса:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
    except Exception as e:
        print(f"❌ Ошибка получения статуса: {e}")
    return False

def main():
    print("🚀 Тестирование российской версии VideoDL")
    print("="*50)
    
    # Проверяем статус
    if test_status():
        print("\n" + "="*50)
        
        # Тестируем YouTube
        if test_russian_youtube():
            print("\n🎉 Российская версия работает!")
        else:
            print("\n⚠️ Нужны дополнительные настройки обхода")
            print("\n💡 Рекомендации:")
            print("   1. Установите VPN")
            print("   2. Смените DNS на 1.1.1.1 или 8.8.8.8")
            print("   3. Попробуйте через мобильный интернет")
    else:
        print("❌ Сервис недоступен")

if __name__ == "__main__":
    main() 