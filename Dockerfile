FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p downloads uploads processed

# Установка переменных окружения
ENV FLASK_APP=app_proxy.py
ENV FLASK_ENV=production
ENV PORT=5000

# Открытие порта
EXPOSE $PORT

# Команда запуска
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 2 app_proxy:app 