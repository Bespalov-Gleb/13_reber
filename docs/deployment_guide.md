# 🚀 Руководство по развертыванию

## 📋 Содержание

1. [Требования к серверу](#требования-к-серверу)
2. [Подготовка сервера](#подготовка-сервера)
3. [Установка зависимостей](#установка-зависимостей)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Настройка приложения](#настройка-приложения)
6. [Docker развертывание](#docker-развертывание)
7. [Настройка веб-сервера](#настройка-веб-сервера)
8. [SSL сертификаты](#ssl-сертификаты)
9. [Настройка мониторинга](#настройка-мониторинга)
10. [Backup стратегия](#backup-стратегия)
11. [Автозапуск сервисов](#автозапуск-сервисов)
12. [Обновление приложения](#обновление-приложения)

---

## 🖥️ Требования к серверу

### 💻 Минимальные требования

- **CPU**: 2 ядра
- **RAM**: 4 GB
- **Диск**: 20 GB SSD
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Сеть**: Статический IP адрес

### 🚀 Рекомендуемые требования

- **CPU**: 4 ядра
- **RAM**: 8 GB
- **Диск**: 50 GB SSD
- **ОС**: Ubuntu 22.04 LTS
- **Сеть**: Статический IP + домен

### ☁️ Рекомендуемые провайдеры

- **DigitalOcean** — Droplet 4GB/2CPU
- **AWS** — t3.medium EC2
- **Google Cloud** — e2-standard-2
- **Vultr** — High Frequency 4GB
- **Hetzner** — CX21

---

## 🔧 Подготовка сервера

### 🐧 Ubuntu 22.04 LTS

#### 📦 Обновление системы

```bash
# Обновить пакеты
sudo apt update && sudo apt upgrade -y

# Установить необходимые пакеты
sudo apt install -y curl wget git vim htop unzip software-properties-common
```

#### 👤 Создание пользователя

```bash
# Создать пользователя для приложения
sudo adduser cafe-bot
sudo usermod -aG sudo cafe-bot

# Переключиться на нового пользователя
su - cafe-bot
```

#### 🔒 Настройка SSH

```bash
# Создать SSH ключи
ssh-keygen -t rsa -b 4096 -C "cafe-bot@yourdomain.com"

# Добавить ключ в authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 🛡️ Настройка firewall

```bash
# Установить ufw
sudo ufw enable

# Разрешить SSH
sudo ufw allow ssh

# Разрешить HTTP и HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Проверить статус
sudo ufw status
```

---

## 📦 Установка зависимостей

### 🐳 Docker и Docker Compose

#### 📥 Установка Docker

```bash
# Удалить старые версии
sudo apt remove docker docker-engine docker.io containerd runc

# Установить зависимости
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавить GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавить репозиторий Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузить сессию
newgrp docker
```

#### 📥 Установка Docker Compose

```bash
# Скачать Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Сделать исполняемым
sudo chmod +x /usr/local/bin/docker-compose

# Проверить установку
docker-compose --version
```

### 🐘 PostgreSQL 14+

#### 📥 Установка PostgreSQL

```bash
# Добавить репозиторий PostgreSQL
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# Установить PostgreSQL
sudo apt update
sudo apt install -y postgresql-14 postgresql-client-14 postgresql-contrib-14
```

#### ⚙️ Настройка PostgreSQL

```bash
# Переключиться на пользователя postgres
sudo -u postgres psql

# Создать базу данных и пользователя
CREATE DATABASE cafe_bot;
CREATE USER cafe_bot_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE cafe_bot TO cafe_bot_user;
\q

# Настроить аутентификацию
sudo vim /etc/postgresql/14/main/pg_hba.conf

# Добавить строку:
local   cafe_bot         cafe_bot_user                    md5

# Перезапустить PostgreSQL
sudo systemctl restart postgresql
```

### 🔴 Redis 6+ (опционально)

#### 📥 Установка Redis

```bash
# Установить Redis
sudo apt install -y redis-server

# Настроить Redis
sudo vim /etc/redis/redis.conf

# Изменить:
bind 127.0.0.1
requirepass your_redis_password

# Перезапустить Redis
sudo systemctl restart redis-server
```

---

## 🗄️ Настройка базы данных

### 📊 Создание базы данных

```bash
# Подключиться к PostgreSQL
psql -h localhost -U cafe_bot_user -d cafe_bot

# Создать расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

# Выйти
\q
```

### 🔄 Миграции

```bash
# Клонировать репозиторий
git clone https://github.com/your-repo/cafe-bot.git
cd cafe-bot

# Установить Python зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Применить миграции
alembic upgrade head
```

---

## ⚙️ Настройка приложения

### 📁 Структура проекта

```bash
# Создать директории
mkdir -p /opt/cafe-bot
mkdir -p /opt/cafe-bot/logs
mkdir -p /opt/cafe-bot/backups
mkdir -p /opt/cafe-bot/ssl

# Скопировать файлы
cp -r cafe-bot/* /opt/cafe-bot/
cd /opt/cafe-bot
```

### 🔧 Конфигурация

#### 📝 Создание config.env

```bash
# Создать файл конфигурации
cp config.env.example config.env
vim config.env
```

#### 📋 Пример config.env

```env
# Основные настройки
BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_telegram_id_here
ADMIN_CHAT_ID=your_admin_chat_id_here

# База данных
DATABASE_URL=postgresql://cafe_bot_user:strong_password_here@localhost:5432/cafe_bot

# Redis (опционально)
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# Режим работы
IS_PRODUCTION=true
LOG_LEVEL=INFO
LOG_FORMAT=json

# Webhook настройки
BOT_WEBHOOK_URL=https://yourdomain.com
BOT_WEBHOOK_PATH=/webhook/bot
WEBHOOK_SECRET=your_webhook_secret_here

# Платежные системы
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_SECRET_KEY=your_secret_key_here
YOOKASSA_WEBHOOK_SECRET=your_webhook_secret_here

# Яндекс.Карты
YANDEX_MAPS_API_KEY=your_api_key_here

# iiko CRM
IIKO_API_URL=https://api-ru.iiko.services
IIKO_API_LOGIN=your_api_login_here
IIKO_ORGANIZATION_ID=your_organization_id_here

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE=/opt/cafe-bot/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

# Настройки кафе
CAFE_NAME=Ваше Кафе
CAFE_ADDRESS=ул. Примерная, д. 1, Москва
CAFE_PHONE=+7 (XXX) XXX-XX-XX
CAFE_EMAIL=info@yourcafe.com

# Рабочее время
WORKING_HOURS_START=10:00
WORKING_HOURS_END=22:00
WORKING_DAYS=1,2,3,4,5,6,7

# Доставка
DELIVERY_FEE=150
MIN_ORDER_AMOUNT=500
DELIVERY_RADIUS_KM=5
```

### 🔐 Права доступа

```bash
# Установить права на файлы
chmod 600 config.env
chmod 600 credentials.json
chown -R cafe-bot:cafe-bot /opt/cafe-bot
```

---

## 🐳 Docker развертывание

### 📝 Docker Compose конфигурация

#### 🐳 docker-compose.prod.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: cafe-bot-app
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://cafe_bot_user:${DB_PASSWORD}@db:5432/cafe_bot
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    env_file:
      - config.env
    volumes:
      - ./logs:/app/logs
      - ./backups:/app/backups
      - ./ssl:/app/ssl
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    networks:
      - cafe-bot-network

  db:
    image: postgres:14
    container_name: cafe-bot-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=cafe_bot
      - POSTGRES_USER=cafe_bot_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - cafe-bot-network

  redis:
    image: redis:6-alpine
    container_name: cafe-bot-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - cafe-bot-network

  nginx:
    image: nginx:alpine
    container_name: cafe-bot-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - cafe-bot-network

volumes:
  postgres_data:
  redis_data:

networks:
  cafe-bot-network:
    driver: bridge
```

#### 🐳 Dockerfile

```dockerfile
FROM python:3.10-slim

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создать рабочую директорию
WORKDIR /app

# Копировать файлы зависимостей
COPY requirements.txt .

# Установить Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копировать исходный код
COPY . .

# Создать пользователя для приложения
RUN useradd -m -u 1000 cafe-bot && chown -R cafe-bot:cafe-bot /app
USER cafe-bot

# Открыть порт
EXPOSE 8000

# Команда запуска
CMD ["python", "-m", "app.main"]
```

### 🚀 Запуск приложения

```bash
# Создать .env файл для Docker Compose
cat > .env << EOF
DB_PASSWORD=strong_password_here
REDIS_PASSWORD=your_redis_password_here
EOF

# Запустить приложение
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f app
```

---

## 🌐 Настройка веб-сервера

### 🔧 Nginx конфигурация

#### 📝 nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Логирование
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Основные настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Безопасность
    server_tokens off;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

    # Upstream для приложения
    upstream cafe_bot_app {
        server app:8000;
    }

    # HTTP сервер (редирект на HTTPS)
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL сертификаты
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL настройки
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # HSTS
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Webhook endpoints
        location /webhook/ {
            limit_req zone=webhook burst=20 nodelay;
            proxy_pass http://cafe_bot_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=50 nodelay;
            proxy_pass http://cafe_bot_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Статические файлы
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://cafe_bot_app;
            access_log off;
        }

        # Блокировка доступа к служебным файлам
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }

        location ~ \.(env|log|sql)$ {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
```

### 🔄 Запуск Nginx

```bash
# Проверить конфигурацию
nginx -t

# Перезапустить Nginx
systemctl restart nginx

# Включить автозапуск
systemctl enable nginx
```

---

## 🔒 SSL сертификаты

### 📜 Let's Encrypt

#### 📥 Установка Certbot

```bash
# Установить Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Проверить автопродление
sudo certbot renew --dry-run
```

#### 🔄 Автопродление

```bash
# Добавить в crontab
sudo crontab -e

# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 🔐 Настройка SSL

#### 📝 Обновление nginx.conf

```nginx
# SSL настройки
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;
```

---

## 📊 Настройка мониторинга

### 📈 Prometheus

#### 📥 Установка Prometheus

```bash
# Создать пользователя
sudo useradd --no-create-home --shell /bin/false prometheus

# Создать директории
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

# Скачать Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz

# Установить файлы
sudo cp prometheus-2.40.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.40.0.linux-amd64/promtool /usr/local/bin/
sudo cp -r prometheus-2.40.0.linux-amd64/consoles /etc/prometheus
sudo cp -r prometheus-2.40.0.linux-amd64/console_libraries /etc/prometheus

# Установить права
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus
```

#### ⚙️ Конфигурация Prometheus

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'cafe-bot'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']
```

#### 🔄 Systemd сервис

```ini
# /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
```

### 📊 Grafana

#### 📥 Установка Grafana

```bash
# Добавить репозиторий Grafana
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Установить Grafana
sudo apt update
sudo apt install -y grafana

# Запустить Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### 📊 Дашборды

1. **Открыть Grafana**: http://yourdomain.com:3000
2. **Войти**: admin/admin
3. **Добавить источник данных**: Prometheus
4. **Импортировать дашборды**:
   - Node Exporter Full
   - PostgreSQL Database
   - Redis Dashboard
   - Nginx Prometheus Exporter

---

## 💾 Backup стратегия

### 🗄️ Backup базы данных

#### 📝 Скрипт backup

```bash
#!/bin/bash
# /opt/cafe-bot/scripts/backup_db.sh

BACKUP_DIR="/opt/cafe-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="cafe_bot"
DB_USER="cafe_bot_user"

# Создать директорию для backup
mkdir -p $BACKUP_DIR

# Создать backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/cafe_bot_$DATE.sql

# Сжать backup
gzip $BACKUP_DIR/cafe_bot_$DATE.sql

# Удалить старые backup (старше 30 дней)
find $BACKUP_DIR -name "cafe_bot_*.sql.gz" -mtime +30 -delete

echo "Backup created: cafe_bot_$DATE.sql.gz"
```

#### 🔄 Автоматический backup

```bash
# Добавить в crontab
crontab -e

# Добавить строку (backup каждый день в 2:00)
0 2 * * * /opt/cafe-bot/scripts/backup_db.sh
```

### 📁 Backup файлов

#### 📝 Скрипт backup файлов

```bash
#!/bin/bash
# /opt/cafe-bot/scripts/backup_files.sh

BACKUP_DIR="/opt/cafe-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/opt/cafe-bot"

# Создать backup
tar -czf $BACKUP_DIR/cafe_bot_files_$DATE.tar.gz \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='venv' \
    --exclude='__pycache__' \
    $SOURCE_DIR

# Удалить старые backup (старше 7 дней)
find $BACKUP_DIR -name "cafe_bot_files_*.tar.gz" -mtime +7 -delete

echo "Files backup created: cafe_bot_files_$DATE.tar.gz"
```

### ☁️ Облачный backup

#### 📤 AWS S3

```bash
# Установить AWS CLI
pip install awscli

# Настроить credentials
aws configure

# Скрипт загрузки в S3
#!/bin/bash
BACKUP_FILE=$1
BUCKET_NAME="your-backup-bucket"

aws s3 cp $BACKUP_FILE s3://$BUCKET_NAME/$(basename $BACKUP_FILE)
```

#### 📤 Google Cloud Storage

```bash
# Установить gsutil
curl https://sdk.cloud.google.com | bash

# Скрипт загрузки в GCS
#!/bin/bash
BACKUP_FILE=$1
BUCKET_NAME="your-backup-bucket"

gsutil cp $BACKUP_FILE gs://$BUCKET_NAME/$(basename $BACKUP_FILE)
```

---

## 🔄 Автозапуск сервисов

### 🔧 Systemd сервисы

#### 📝 Сервис приложения

```ini
# /etc/systemd/system/cafe-bot.service
[Unit]
Description=Cafe Bot Application
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=cafe-bot
Group=cafe-bot
WorkingDirectory=/opt/cafe-bot
Environment=PATH=/opt/cafe-bot/venv/bin
ExecStart=/opt/cafe-bot/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 🔄 Активация сервисов

```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable cafe-bot
sudo systemctl enable postgresql
sudo systemctl enable redis-server
sudo systemctl enable nginx

# Запустить сервисы
sudo systemctl start cafe-bot
```

### 📊 Мониторинг сервисов

#### 🔍 Скрипт проверки

```bash
#!/bin/bash
# /opt/cafe-bot/scripts/health_check.sh

# Проверить статус сервисов
services=("cafe-bot" "postgresql" "redis-server" "nginx")

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
        # Отправить уведомление
        curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
            -d "chat_id=$ADMIN_CHAT_ID" \
            -d "text=🚨 Service $service is down!"
    fi
done
```

#### 🔄 Автоматическая проверка

```bash
# Добавить в crontab
crontab -e

# Проверка каждые 5 минут
*/5 * * * * /opt/cafe-bot/scripts/health_check.sh
```

---

## 🔄 Обновление приложения

### 📥 Обновление кода

#### 🔄 Скрипт обновления

```bash
#!/bin/bash
# /opt/cafe-bot/scripts/update.sh

cd /opt/cafe-bot

# Создать backup
./scripts/backup_db.sh
./scripts/backup_files.sh

# Остановить приложение
sudo systemctl stop cafe-bot

# Обновить код
git pull origin main

# Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt

# Применить миграции
alembic upgrade head

# Запустить приложение
sudo systemctl start cafe-bot

echo "Application updated successfully"
```

### 🐳 Обновление Docker

#### 🔄 Скрипт обновления Docker

```bash
#!/bin/bash
# /opt/cafe-bot/scripts/update_docker.sh

cd /opt/cafe-bot

# Создать backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U cafe_bot_user cafe_bot > backup_$(date +%Y%m%d_%H%M%S).sql

# Остановить приложение
docker-compose -f docker-compose.prod.yml down

# Обновить образы
docker-compose -f docker-compose.prod.yml pull

# Запустить приложение
docker-compose -f docker-compose.prod.yml up -d

echo "Docker application updated successfully"
```

### 🔄 Blue-Green развертывание

#### 📝 Скрипт Blue-Green

```bash
#!/bin/bash
# /opt/cafe-bot/scripts/blue_green_deploy.sh

# Создать новую версию
docker-compose -f docker-compose.prod.yml -p cafe-bot-green up -d

# Проверить здоровье
sleep 30
if curl -f http://localhost:8001/health; then
    # Переключить трафик
    docker-compose -f docker-compose.prod.yml -p cafe-bot-blue down
    docker-compose -f docker-compose.prod.yml -p cafe-bot-green -p cafe-bot up -d
    echo "Deployment successful"
else
    # Откатить изменения
    docker-compose -f docker-compose.prod.yml -p cafe-bot-green down
    echo "Deployment failed, rolled back"
fi
```

---

## 🆘 Troubleshooting

### ❌ Проблемы с запуском

#### 🔍 Проверка логов

```bash
# Логи приложения
journalctl -u cafe-bot -f

# Логи Docker
docker-compose -f docker-compose.prod.yml logs -f app

# Логи Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

#### 🔧 Диагностика

```bash
# Проверить статус сервисов
systemctl status cafe-bot postgresql redis-server nginx

# Проверить порты
netstat -tlnp | grep :8000
netstat -tlnp | grep :5432
netstat -tlnp | grep :6379

# Проверить дисковое пространство
df -h

# Проверить память
free -h
```

### 🔄 Восстановление из backup

#### 📥 Восстановление базы данных

```bash
# Остановить приложение
sudo systemctl stop cafe-bot

# Восстановить базу данных
gunzip -c /opt/cafe-bot/backups/cafe_bot_20240101_020000.sql.gz | psql -h localhost -U cafe_bot_user -d cafe_bot

# Запустить приложение
sudo systemctl start cafe-bot
```

#### 📁 Восстановление файлов

```bash
# Остановить приложение
sudo systemctl stop cafe-bot

# Восстановить файлы
tar -xzf /opt/cafe-bot/backups/cafe_bot_files_20240101_020000.tar.gz -C /

# Запустить приложение
sudo systemctl start cafe-bot
```

---

## 📞 Поддержка

### 🆘 Техническая поддержка

- **📧 Email**: support@example.com
- **📱 Telegram**: @support_bot
- **🌐 Сайт**: https://support.example.com

### 📚 Дополнительные ресурсы

- **📖 Документация**: https://docs.example.com
- **🎥 Видеоуроки**: https://tutorials.example.com
- **💬 Сообщество**: https://community.example.com

### 🔄 Обновления

- **📢 Новости**: Подпишитесь на канал обновлений
- **🐛 Баг-репорты**: Сообщайте об ошибках
- **💡 Предложения**: Предлагайте улучшения

---

*Руководство обновлено: {{ current_date }}*
