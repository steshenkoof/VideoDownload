# 🌐 Где получить PROXY для обхода блокировок

## 🆓 Бесплатные публичные proxy:

### **1. Списки бесплатных proxy:**

- **https://free-proxy-list.net/**
- **https://www.proxy-list.download/**
- **https://www.proxynova.com/proxy-server-list/**
- **https://spys.one/free-proxy-list/**

### **2. Формат proxy URL:**

```
http://IP:PORT
socks5://IP:PORT
```

**Примеры:**

```
http://103.152.112.145:80
http://181.78.18.219:999
socks5://123.45.67.89:1080
```

## 💰 Платные надежные proxy:

### **1. Рекомендуемые сервисы:**

- **Bright Data** (luminati.io) - $500+/месяц
- **Oxylabs** - от $300/месяц
- **ProxyMesh** - от $10/месяц
- **Storm Proxies** - от $50/месяц

### **2. Более доступные:**

- **ProxyRack** - от $49/месяц
- **MyPrivateProxy** - от $2.49/proxy
- **SSLPrivateProxy** - от $1.77/proxy

## 🔧 Как использовать в нашем приложении:

### **Вариант 1: Автоматический поиск**

Приложение само найдет рабочий proxy из встроенного списка:

```bash
python app_proxy.py
```

### **Вариант 2: Свой proxy**

Укажите свой proxy в интерфейсе или в коде:

```python
# В app_proxy.py измените:
PROXY_CONFIG = {
    'http_proxy': 'http://ваш-proxy:порт',
    'enabled': True
}
```

### **Вариант 3: Через JSON API**

```json
{
  "url": "https://www.tiktok.com/@username/video/123",
  "proxy": "http://103.152.112.145:80"
}
```

## 🎯 Для хостинга (решение проблемы пользователей):

### **1. VPS в разрешенных странах:**

- **США:** DigitalOcean, Linode, Vultr ($5-10/месяц)
- **Европа:** Hetzner, Contabo ($3-15/месяц)
- **Азия:** Vultr Singapore, DigitalOcean Singapore

### **2. Настройка на сервере:**

```bash
# Установка на Ubuntu/Debian
git clone https://github.com/steshenkoof/VideoDownload.git
cd VideoDownload
pip install -r requirements.txt
python app_proxy.py

# Или app_russia_v2.py с VPN на сервере
```

### **3. Cloudflare для дополнительной маскировки:**

- Зарегистрируйтесь на cloudflare.com
- Добавьте домен и настройте DNS
- Включите SSL и кэширование

## 🔍 Проверка IP после настройки:

### **Команды для проверки:**

```bash
# Текущий IP
curl ipinfo.io

# Через proxy
curl --proxy http://your-proxy:port ipinfo.io

# В браузере
# Откройте whatismyipaddress.com
```

## ⚡ Быстрое решение прямо сейчас:

### **1. Используйте встроенные proxy:**

```bash
python app_proxy.py  # Порт 5002
```

### **2. Или настройте системный VPN + наше приложение:**

```bash
python app_russia_v2.py  # Порт 5001
```

### **3. Проверьте работу:**

Попробуйте ту же проблемную ссылку:

```
https://www.tiktok.com/@maligoshik/video/7501009948856306949
```

## 🚀 Для продакшена:

1. **Арендуйте VPS за пределами России**
2. **Установите там приложение**
3. **Настройте домен через Cloudflare**
4. **Все пользователи смогут скачивать без VPN!**

**Стоимость:** $5-15/месяц за сервер
