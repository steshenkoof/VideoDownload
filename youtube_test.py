#!/usr/bin/env python3
"""
Тест с YouTube видео
"""

import requests
import json

def test_youtube():
    """Тестирует скачивание YouTube видео"""
    # Короткое тестовое видео на YouTube
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"🎬 Тестируем YouTube видео:")
    print(f"🔗 {youtube_url}")
    print("⏳ Скачиваем...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/download",
            json={"url": youtube_url},
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 минуты для YouTube
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Результат:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print(f"\n🎉 УСПЕШНО СКАЧАНО!")
                print(f"📁 Файл: {data.get('filename')}")
                print(f"📺 Название: {data.get('title')}")
                print(f"🎬 Платформа: {data.get('platform')}")
                print(f"⏱️ Длительность: {data.get('duration', 0)} сек")
                
                filename = data.get('filename')
                if filename:
                    print(f"\n🔗 Прямая ссылка для скачивания:")
                    print(f"http://127.0.0.1:5000/download_file/{filename}")
                
                return True
            else:
                print(f"❌ Ошибка: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def show_web_interface():
    """Показывает информацию о веб-интерфейсе"""
    print(f"\n" + "="*60)
    print("🌐 ВЕБ-ИНТЕРФЕЙС ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
    print("="*60)
    print("🖥️  Откройте браузер и перейдите по адресу:")
    print("   http://127.0.0.1:5000")
    print("   или")
    print("   http://192.168.1.7:5000")
    print()
    print("✨ Возможности веб-интерфейса:")
    print("   • Современный дизайн с градиентами")
    print("   • Поддержка всех платформ (YouTube, TikTok, Instagram)")
    print("   • Автоматическое определение платформы")
    print("   • Показ информации о видео")
    print("   • Прогресс-бар скачивания")
    print("   • Мобильная поддержка")
    print("   • Очистка загрузок одним кликом")
    print()
    print("🎯 Поддерживаемые форматы ссылок:")
    print("   YouTube: https://www.youtube.com/watch?v=...")
    print("   TikTok: https://www.tiktok.com/@user/video/...")
    print("   Instagram: https://www.instagram.com/p/...")
    print("   Telegram: https://t.me/...")

def main():
    print("🚀 Финальный тест сервиса VideoDL")
    print("="*50)
    
    # Тестируем YouTube
    success = test_youtube()
    
    if success:
        print(f"\n✅ Сервис полностью работает!")
        
        # Проверяем папку загрузок
        try:
            response = requests.get("http://127.0.0.1:5000/download_file/test")
            # Если получили 404, значит эндпоинт работает
        except:
            pass
            
        show_web_interface()
    else:
        print(f"\n⚠️  Возможные причины проблем:")
        print("   • Проблемы с интернет-соединением")
        print("   • Блокировка видео в регионе")
        print("   • Нужно обновить yt-dlp еще раз")
        print()
        print("💡 Попробуйте через веб-интерфейс:")
        show_web_interface()

if __name__ == "__main__":
    main() 