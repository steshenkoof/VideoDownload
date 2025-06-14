import requests
import json

url = "http://127.0.0.1:5001/download"
data = {
    "url": "https://www.tiktok.com/@chardotv/video/7498042844419017989?is_from_webapp=1&sender_device=pc"
}

print("🎯 Пытаемся скачать TikTok видео...")
print(f"📹 URL: {data['url']}")
print("⏳ Отправляем запрос...")

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"📊 Статус: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Ответ получен:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('success'):
            print(f"🎉 Успех! Файл: {result.get('filename')}")
            if result.get('info'):
                info = result['info']
                print(f"📝 Название: {info.get('title', 'Неизвестно')}")
                print(f"👤 Автор: {info.get('uploader', 'Неизвестно')}")
                print(f"⏱️ Длительность: {info.get('duration', 'Неизвестно')} сек")
        else:
            print(f"❌ Ошибка: {result.get('error')}")
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"🚫 Ошибка соединения: {e}") 