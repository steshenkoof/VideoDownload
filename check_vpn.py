#!/usr/bin/env python3
"""
🌐 Скрипт проверки VPN подключения
Проверяет ваш текущий IP адрес и страну
"""

import requests
import json
from datetime import datetime

def check_ip_and_location():
    """Проверяет текущий IP адрес и местоположение"""
    print("🔍 Проверяем ваш текущий IP адрес...")
    
    try:
        # Проверяем IP через несколько сервисов для надежности
        services = [
            ("ipapi.co", "https://ipapi.co/json/"),
            ("ipinfo.io", "https://ipinfo.io/json"),
            ("httpbin.org", "https://httpbin.org/ip")
        ]
        
        for service_name, url in services:
            try:
                print(f"📡 Проверяем через {service_name}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if service_name == "ipapi.co":
                        ip = data.get('ip', 'Неизвестно')
                        country = data.get('country_name', 'Неизвестно')
                        city = data.get('city', 'Неизвестно')
                        org = data.get('org', 'Неизвестно')
                        
                        print(f"✅ {service_name} результат:")
                        print(f"   🌐 IP: {ip}")
                        print(f"   🏳️ Страна: {country}")
                        print(f"   🏙️ Город: {city}")
                        print(f"   🏢 Провайдер: {org}")
                        
                        # Проверяем, российский ли IP  
                        is_russian = country.lower() in ['russia', 'russian federation', 'россия']
                        if is_russian:
                            print("   ❌ ВНИМАНИЕ: Вы используете российский IP!")
                            print("   🚫 TikTok и YouTube могут быть заблокированы")
                            print("   💡 Рекомендуется подключить VPN")
                        else:
                            print(f"   ✅ Отлично! IP не российский ({country})")
                            print("   🎉 TikTok и YouTube должны работать!")
                        
                        return not is_russian
                        
                    elif service_name == "ipinfo.io":
                        ip = data.get('ip', 'Неизвестно')
                        country = data.get('country', 'Неизвестно')
                        city = data.get('city', 'Неизвестно')
                        org = data.get('org', 'Неизвестно')
                        
                        print(f"✅ {service_name} результат:")
                        print(f"   🌐 IP: {ip}")
                        print(f"   🏳️ Страна: {country}")
                        print(f"   🏙️ Город: {city}")
                        print(f"   🏢 Провайдер: {org}")
                        
                    elif service_name == "httpbin.org":
                        ip = data.get('origin', 'Неизвестно')
                        print(f"✅ {service_name} результат:")
                        print(f"   🌐 IP: {ip}")
                        
                else:
                    print(f"   ❌ Ошибка: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   🚫 Ошибка подключения к {service_name}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Общая ошибка при проверке IP: {e}")
        return False

def test_access_to_blocked_sites():
    """Тестирует доступ к заблокированным сайтам"""
    print("\n🧪 Тестируем доступ к заблокированным сайтам...")
    
    test_sites = [
        ("TikTok", "https://www.tiktok.com"),
        ("YouTube", "https://www.youtube.com"),
        ("Instagram", "https://www.instagram.com")
    ]
    
    results = {}
    
    for site_name, url in test_sites:
        try:
            print(f"🔍 Проверяем {site_name}...")
            response = requests.get(url, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 301, 302]:
                print(f"   ✅ {site_name}: Доступен! (код {response.status_code})")
                results[site_name] = True
            else:
                print(f"   ⚠️ {site_name}: Возможны проблемы (код {response.status_code})")
                results[site_name] = False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {site_name}: Заблокирован или недоступен ({e})")
            results[site_name] = False
    
    return results

def print_recommendations(vpn_active, site_results):
    """Выводит рекомендации на основе результатов"""
    print("\n" + "="*50)
    print("📋 РЕКОМЕНДАЦИИ:")
    print("="*50)
    
    if vpn_active:
        print("✅ VPN активен - отлично!")
        print("🎯 Можете запускать наш сервис:")
        print("   python app_russia_v2.py")
        print("   Откройте: http://127.0.0.1:5001")
        
        if all(site_results.values()):
            print("🎉 Все сайты доступны - можете скачивать видео!")
        else:
            blocked = [site for site, accessible in site_results.items() if not accessible]
            print(f"⚠️ Некоторые сайты недоступны: {', '.join(blocked)}")
            print("💡 Попробуйте сменить сервер VPN на американский")
    else:
        print("❌ VPN НЕ активен!")
        print("🚫 TikTok и YouTube заблокированы в России")
        print("\n📋 ЧТО ДЕЛАТЬ:")
        print("1. 📥 Скачайте ProtonVPN: https://protonvpn.com/")
        print("2. 📝 Зарегистрируйтесь (бесплатно)")
        print("3. 🇺🇸 Подключитесь к серверу в США")
        print("4. 🔄 Запустите этот скрипт снова")
        print("5. ✅ Запускайте наш сервис после подключения VPN")

def main():
    """Основная функция"""
    print("🌐 VPN ПРОВЕРКА - Сервис загрузки видео")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # Проверяем IP и местоположение
    vpn_active = check_ip_and_location()
    
    # Тестируем доступ к сайтам
    site_results = test_access_to_blocked_sites()
    
    # Выводим рекомендации
    print_recommendations(vpn_active, site_results)
    
    print("\n🔧 Для настройки VPN смотрите файл: VPN_SETUP_GUIDE.md")

if __name__ == "__main__":
    main() 