#!/usr/bin/env python3
"""
🚀 Быстрая проверка VPN подключения
"""

import requests
import time

def quick_ip_check():
    """Быстро проверяет текущий IP"""
    try:
        print("🔍 Проверяем ваш IP...")
        response = requests.get("https://ipapi.co/json/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip')
            country = data.get('country_name')
            city = data.get('city')
            
            print(f"🌐 IP: {ip}")
            print(f"🏳️ Страна: {country}")
            print(f"🏙️ Город: {city}")
            
            is_russian = country.lower() in ['russia', 'russian federation']
            if is_russian:
                print("❌ Все еще российский IP! VPN не подключен.")
                return False
            else:
                print(f"✅ Отлично! VPN работает! ({country})")
                return True
        else:
            print("❌ Ошибка при проверке IP")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_tiktok_access():
    """Быстро тестирует доступ к TikTok"""
    try:
        print("\n🧪 Тестируем TikTok...")
        response = requests.get("https://www.tiktok.com", timeout=10)
        if response.status_code == 200:
            print("✅ TikTok доступен!")
            return True
        else:
            print(f"⚠️ TikTok проблемы (код {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ TikTok недоступен: {e}")
        return False

def main():
    print("🚀 БЫСТРАЯ ПРОВЕРКА VPN")
    print("="*30)
    
    # Проверяем IP
    vpn_ok = quick_ip_check()
    
    if vpn_ok:
        # Тестируем TikTok
        tiktok_ok = test_tiktok_access()
        
        if tiktok_ok:
            print("\n🎉 ВСЕ ГОТОВО!")
            print("✅ VPN подключен")
            print("✅ TikTok доступен")
            print("\n🎯 МОЖЕТЕ ЗАПУСКАТЬ СЕРВИС:")
            print("python app_russia_v2.py")
            print("Откройте: http://127.0.0.1:5001")
        else:
            print("\n⚠️ VPN подключен, но TikTok не работает")
            print("💡 Попробуйте сменить сервер VPN")
    else:
        print("\n❌ VPN НЕ ПОДКЛЮЧЕН!")
        print("📋 ЧТО ДЕЛАТЬ:")
        print("1. Убедитесь что ProtonVPN запущен")
        print("2. Выберите сервер в США")
        print("3. Нажмите Connect")
        print("4. Запустите этот скрипт снова")

if __name__ == "__main__":
    main() 