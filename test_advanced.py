#!/usr/bin/env python3
import requests
import json
import time

def test_advanced_tiktok():
    """Тестирует продвинутую версию с TikTok"""
    tiktok_url = "https://www.tiktok.com/@b2zfamily/video/7513864181188365591?is_from_webapp=1&sender_device=pc"
    
    print("🇷🇺 Тестируем ПРОДВИНУТУЮ версию v2.0 с TikTok")
    print(f"🔗 URL: {tiktok_url}")
    print("⏳ Пробуем 4 метода обхода...")
    
    try:
        # Ждем немного чтобы сервер запустился
        time.sleep(3)
        
        response = requests.post(
            "http://127.0.0.1:5001/download",  # Порт 5001!
            json={"url": tiktok_url},
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Результат:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print(f"\n🎉 УСПЕХ! Метод: {data.get('method', 'unknown')}")
                print(f"📁 Файл: {data.get('filename')}")
                print(f"📺 Название: {data.get('title')}")
                return True
            else:
                print(f"\n❌ Все методы не сработали")
                suggestions = data.get('suggestions', [])
                if suggestions:
                    print("💡 Рекомендации:")
                    for suggestion in suggestions:
                        print(f"   {suggestion}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_status():
    """Проверяем статус продвинутой версии"""
    try:
        time.sleep(2)  # Ждем запуска сервера
        response = requests.get("http://127.0.0.1:5001/status")
        if response.status_code == 200:
            data = response.json()
            print("🚀 Статус продвинутой версии v2.0:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
    except Exception as e:
        print(f"❌ Сервер не отвечает: {e}")
        return False

def main():
    print("🚀 ТЕСТИРОВАНИЕ ПРОДВИНУТОЙ РОССИЙСКОЙ ВЕРСИИ v2.0")
    print("="*60)
    
    if test_status():
        print("\n" + "="*60)
        success = test_advanced_tiktok()
        
        if success:
            print("\n🎊 ПОЗДРАВЛЯЕМ! Продвинутые методы сработали!")
            print("🌐 Откройте http://127.0.0.1:5001 в браузере")
        else:
            print("\n📝 ИТОГ: Нужны дополнительные средства обхода")
            print("\n🛡️ Для 100% работы TikTok рекомендуем:")
            print("   1. 🌐 VPN (ProtonVPN, Windscribe - бесплатно)")
            print("   2. 📱 Мобильный интернет (другой провайдер)")
            print("   3. 🔧 DNS 1.1.1.1 + VPN")
            print("   4. 🏢 Корпоративная сеть")
            
        print(f"\n✅ ЧТО УЖЕ РАБОТАЕТ:")
        print("   • Веб-интерфейс на порту 5001")
        print("   • API с множественными методами обхода")
        print("   • Автоматическое определение платформ")
        print("   • 4 метода для TikTok + 3 для YouTube")
        
    else:
        print("❌ Продвинутая версия не запустилась")
        print("💡 Попробуйте: python app_russia_v2.py")

if __name__ == "__main__":
    main() 