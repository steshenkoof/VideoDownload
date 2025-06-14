#!/usr/bin/env python3
import requests
import json

# TikTok ссылка от пользователя
tiktok_url = "https://www.tiktok.com/@b2zfamily/video/7513864181188365591?is_from_webapp=1&sender_device=pc"

print("🇷🇺 Тестируем российскую версию с TikTok")
print(f"🔗 URL: {tiktok_url}")

try:
    response = requests.post(
        "http://127.0.0.1:5000/download",
        json={"url": tiktok_url},
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Результат:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success'):
            print(f"\n🎉 УСПЕХ! Файл: {data.get('filename')}")
            print(f"📺 Название: {data.get('title')}")
        else:
            print(f"\n❌ Ошибка: {data.get('error')}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")

except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "="*50)
print("💡 Если не работает, попробуйте:")
print("1. Включить VPN")
print("2. Сменить DNS на 1.1.1.1")
print("3. Использовать мобильный интернет") 