# 🔌 Руководство по интеграциям

## 📋 Содержание

1. [Обзор интеграций](#обзор-интеграций)
2. [Платежные системы](#платежные-системы)
3. [Картографические сервисы](#картографические-сервисы)
4. [CRM системы](#crm-системы)
5. [Аналитика и отчеты](#аналитика-и-отчеты)
6. [Webhook endpoints](#webhook-endpoints)
7. [Безопасность](#безопасность)
8. [Мониторинг и логирование](#мониторинг-и-логирование)
9. [Troubleshooting](#troubleshooting)

---

## 🌐 Обзор интеграций

Telegram Bot для кафе интегрируется с множеством внешних сервисов для обеспечения полного функционала:

### 💳 Платежные системы
- **ЮKassa** — основная платежная система
- **CloudPayments** — резервная система
- **Stripe** — международные платежи

### 🗺️ Картографические сервисы
- **Яндекс.Карты** — автоподсказки адресов, геокодирование
- **Google Maps** — альтернативный сервис

### 📊 CRM и аналитика
- **iiko** — синхронизация меню и заказов
- **Google Sheets** — экспорт аналитики

### 📱 Уведомления
- **Telegram Bot API** — основной канал связи
- **Webhook** — интеграция с внешними сервисами

---

## 💳 Платежные системы

### 🏦 ЮKassa (основная система)

#### 📋 Регистрация в ЮKassa

1. **Перейдите на сайт**: https://yookassa.ru
2. **Зарегистрируйтесь** как юридическое лицо или ИП
3. **Подтвердите документы** и пройдите верификацию
4. **Получите доступ** к личному кабинету

#### 🔑 Получение ключей

1. **Войдите в личный кабинет** ЮKassa
2. **Перейдите в раздел "Настройки"**
3. **Скопируйте Shop ID** (идентификатор магазина)
4. **Сгенерируйте Secret Key** (секретный ключ)

#### ⚙️ Настройка в боте

Добавьте в `config.env`:

```env
# ЮKassa настройки
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_SECRET_KEY=your_secret_key_here
YOOKASSA_WEBHOOK_SECRET=your_webhook_secret_here
```

#### 🌐 Настройка Webhook

1. **В личном кабинете ЮKassa** перейдите в "Настройки" → "Webhook"
2. **Укажите URL**: `https://yourdomain.com/webhook/yookassa`
3. **Выберите события**:
   - `payment.succeeded` — успешная оплата
   - `payment.canceled` — отмена платежа
   - `payment.waiting_for_capture` — ожидание подтверждения
4. **Сохраните настройки**

#### 🧪 Тестирование в Sandbox

1. **Включите тестовый режим** в личном кабинете
2. **Используйте тестовые карты**:
   - **Успешная оплата**: `5555 5555 5555 4444`
   - **Неуспешная оплата**: `5555 5555 5555 4445`
   - **CVV**: `123`
   - **Срок**: любая будущая дата
3. **Проверьте обработку** платежей в боте

#### 🚀 Переход в Production

1. **Отключите тестовый режим** в ЮKassa
2. **Обновите настройки** в `config.env`
3. **Проверьте работу** с реальными платежами
4. **Настройте мониторинг** платежей

### ☁️ CloudPayments (резервная система)

#### 📋 Регистрация в CloudPayments

1. **Перейдите на сайт**: https://cloudpayments.ru
2. **Зарегистрируйтесь** и пройдите верификацию
3. **Получите доступ** к личному кабинету

#### 🔑 Получение ключей

1. **Войдите в личный кабинет** CloudPayments
2. **Перейдите в "Настройки" → "API"**
3. **Скопируйте Public ID** (публичный идентификатор)
4. **Скопируйте API Secret** (секретный ключ API)

**Примечание:** CloudPayments использует HMAC-SHA256 подпись для аутентификации запросов.

#### ⚙️ Настройка в боте

Добавьте в `config.env`:

```env
# CloudPayments настройки
CLOUDPAYMENTS_PUBLIC_ID=your_public_id_here
CLOUDPAYMENTS_API_SECRET=your_api_secret_here
```

#### 🌐 Настройка Webhook

1. **В личном кабинете** перейдите в "Настройки" → "Webhook"
2. **Укажите URL**: `https://yourdomain.com/webhook/cloudpayments`
3. **Выберите события**:
   - `Check` — проверка платежа
   - `Pay` — успешная оплата
   - `Fail` — неуспешная оплата
4. **Сохраните настройки**

### 💳 Stripe (международные платежи)

#### 📋 Регистрация в Stripe

1. **Перейдите на сайт**: https://stripe.com
2. **Зарегистрируйтесь** и пройдите верификацию
3. **Получите доступ** к Dashboard

#### 🔑 Получение ключей

1. **Войдите в Dashboard** Stripe
2. **Перейдите в "Developers" → "API keys"**
3. **Скопируйте Publishable key** (публичный ключ)
4. **Скопируйте Secret key** (секретный ключ)

#### ⚙️ Настройка в боте

Добавьте в `config.env`:

```env
# Stripe настройки
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

---

## 🗺️ Картографические сервисы

### 🗺️ Яндекс.Карты

#### 🔑 Получение API ключа

1. **Перейдите на сайт**: https://developer.tech.yandex.ru
2. **Войдите через Яндекс ID**
3. **Создайте новый проект**
4. **Выберите API**:
   - **JavaScript API** — для веб-интерфейса
   - **HTTP API** — для серверных запросов
5. **Получите API ключ**

#### ⚙️ Настройка в боте

Добавьте в `config.env`:

```env
# Яндекс.Карты настройки
YANDEX_MAPS_API_KEY=your_api_key_here
```

**Примечание:** URL для API эндпоинтов настраиваются автоматически в коде. Дополнительные URL настройки не требуются.

#### 📍 Настройка геокодирования

1. **Укажите адрес кафе** для расчета доставки
2. **Настройте зону доставки** (радиус в километрах)
3. **Проверьте работу** автоподсказок адресов

#### 🚚 Настройка доставки

```env
# Настройки доставки
CAFE_ADDRESS=ул. Примерная, д. 1, Москва
DELIVERY_RADIUS_KM=5
DELIVERY_FEE=150
MIN_ORDER_AMOUNT=500
```

### 🗺️ Google Maps (альтернатива)

#### 🔑 Получение API ключа

1. **Перейдите в Google Cloud Console**: https://console.cloud.google.com
2. **Создайте новый проект**
3. **Включите API**:
   - **Maps JavaScript API**
   - **Geocoding API**
   - **Places API**
4. **Создайте API ключ**

#### ⚙️ Настройка в боте

Добавьте в `config.env`:

```env
# Google Maps настройки
GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Примечание:** URL для API эндпоинтов настраиваются автоматически в коде. Дополнительные URL настройки не требуются.

---

## 📊 CRM системы

### 🍽️ iiko CRM

#### 📋 Получение доступа к iiko API

1. **Войдите в iikoWeb** (веб-интерфейс iiko)
2. **Перейдите в настройки API**
3. **Создайте API-логин**:
   - Дайте ключу понятное название (например, "API для Telegram бота")
   - Укажите email для уведомлений
   - Оставьте поле "Источник заказа" пустым
4. **Получите API-логин** (это строка, похожая на API-ключ)
5. **Получите Organization ID** — идентификатор организации (опционально)

**Примечание:** iiko API использует только API-логин для аутентификации. Пароль не требуется.

#### ⚙️ Настройка в боте

Добавьте в `config.env`:

```env
# iiko API настройки
IIKO_API_URL=https://api-ru.iiko.services
IIKO_API_LOGIN=your_api_login_here
IIKO_ORGANIZATION_ID=your_organization_id_here  # Опционально, будет получен автоматически
```

#### 🔄 Синхронизация меню

1. **В админ-панели** перейдите в "🍽️ iiko CRM"
2. **Нажмите "🔄 Синхронизировать меню"**
3. **Проверьте результат** синхронизации
4. **Настройте автоматическую синхронизацию** (каждый час)

#### 📋 Отправка заказов в iiko

1. **При создании заказа** он автоматически отправляется в iiko
2. **Проверьте статус** отправки в логах
3. **Настройте уведомления** о статусах заказов

#### ✅ Обязательный flow iiko Cloud API

Для корректной работы интеграции используйте последовательность:

1. `POST /api/1/access_token` с body `{"apiLogin":"..."}`
2. `POST /api/1/organizations` для получения `organizationId`
3. `POST /api/1/terminal_groups` для получения `terminalGroupId`
4. `POST /api/1/deliveries/order_types` для получения корректного `orderTypeId`
5. `POST /api/1/payment_types` для получения корректного `paymentTypeId`
6. `POST /api/1/deliveries/create` с обязательными полями `organizationId`, `terminalGroupId`, `order.orderTypeId`, `order.payments[].paymentTypeId`
7. `POST /api/1/commands/status` для проверки результата асинхронной операции по `correlationId`

Важно:
- Для `organizations` используется именно `POST`, не `GET`.
- В `deliveries/create` нельзя подставлять строковые значения `"delivery"`/`"pickup"` вместо реального `orderTypeId`.
- `paymentTypeId` не должен быть `null` в production-сценарии.
- Ответ `deliveries/create` нужно считать асинхронной командой и подтверждать через `commands/status`.

#### ⚙️ Настройка терминала

1. **В iiko** настройте терминал для приема заказов
2. **Укажите тип заказа** (доставка/самовывоз)
3. **Настройте маппинг** блюд между системами

### 📊 Google Sheets

#### 🔑 Создание Service Account

1. **Перейдите в Google Cloud Console**: https://console.cloud.google.com
2. **Создайте новый проект** или выберите существующий
3. **Включите Google Sheets API**
4. **Создайте Service Account**:
   - Перейдите в "IAM & Admin" → "Service Accounts"
   - Нажмите "Create Service Account"
   - Укажите имя и описание
   - Создайте ключ (JSON файл)

#### 📊 Создание таблицы

1. **Создайте новую Google Таблицу**
2. **Настройте структуру**:
   - **Лист "Заказы"** — информация о заказах
   - **Лист "Статистика"** — ежедневная статистика
   - **Лист "Пользователи"** — информация о клиентах
3. **Поделитесь таблицей** с Service Account

#### ⚙️ Настройка в боте

1. **Скопируйте JSON файл** Service Account в папку проекта
2. **Добавьте в `config.env`**:

```env
# Google Sheets настройки
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

3. **Проверьте доступ** к таблице

#### 📈 Структура таблицы

**Лист "Заказы":**
| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| Дата | Время | Номер заказа | Клиент | Телефон | Адрес | Сумма | Статус | Способ оплаты |

**Лист "Статистика":**
| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Дата | Заказов | Выручка | Средний чек | Новых клиентов | Популярное блюдо |

---

## 🌐 Webhook endpoints

### 🔧 Настройка nginx

#### 📝 Конфигурация nginx

Создайте файл `/etc/nginx/sites-available/cafe-bot`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Webhook endpoints
    location /webhook/yookassa {
        proxy_pass http://localhost:8000/webhook/yookassa;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /webhook/cloudpayments {
        proxy_pass http://localhost:8000/webhook/cloudpayments;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /webhook/stripe {
        proxy_pass http://localhost:8000/webhook/stripe;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 🔄 Активация конфигурации

```bash
# Создать символическую ссылку
sudo ln -s /etc/nginx/sites-available/cafe-bot /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Перезагрузить nginx
sudo systemctl reload nginx
```

### 🔒 SSL сертификаты (Let's Encrypt)

#### 📋 Установка Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

#### 🔑 Получение сертификата

```bash
# Получить сертификат
sudo certbot --nginx -d yourdomain.com

# Автоматическое обновление
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 🧪 Тестирование webhook

#### 🔍 Проверка доступности

```bash
# Проверить доступность webhook
curl -X POST https://yourdomain.com/webhook/yookassa \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

#### 📊 Мониторинг webhook

1. **Проверьте логи nginx**:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

2. **Проверьте логи приложения**:
```bash
docker-compose logs -f app
```

---

## 🔒 Безопасность

### 🛡️ Защита webhook

#### 🔐 Проверка подписи

Все webhook должны проверять подпись запроса:

```python
def verify_webhook_signature(payload, signature, secret):
    """Проверка подписи webhook."""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

#### 🔒 HTTPS обязателен

- Все webhook должны работать только по HTTPS
- Используйте SSL сертификаты от Let's Encrypt
- Настройте HSTS заголовки

#### 🚫 Защита от DDoS

```nginx
# Ограничение запросов
limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;

location /webhook/ {
    limit_req zone=webhook burst=20 nodelay;
    # ... остальная конфигурация
}
```

### 🔐 Защита API ключей

#### 📁 Хранение ключей

- **Никогда не коммитьте** ключи в Git
- **Используйте переменные окружения**
- **Ротируйте ключи** регулярно
- **Ограничьте доступ** к ключам

#### 🔄 Ротация ключей

1. **Создайте новые ключи** в сервисах
2. **Обновите конфигурацию** в `config.env`
3. **Перезапустите приложение**
4. **Удалите старые ключи**

### 🛡️ Защита базы данных

#### 🔒 Настройка PostgreSQL

```sql
-- Создание пользователя с ограниченными правами
CREATE USER cafe_bot_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE cafe_bot TO cafe_bot_user;
GRANT USAGE ON SCHEMA public TO cafe_bot_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cafe_bot_user;
```

#### 🔐 Шифрование данных

- **Шифруйте чувствительные данные** (пароли, токены)
- **Используйте bcrypt** для хеширования паролей
- **Настройте SSL** для подключения к БД

---

## 📊 Мониторинг и логирование

### 📈 Мониторинг системы

#### 🔍 Prometheus метрики

```python
from prometheus_client import Counter, Histogram, Gauge

# Метрики
orders_total = Counter('orders_total', 'Total orders', ['status'])
order_duration = Histogram('order_duration_seconds', 'Order processing time')
active_users = Gauge('active_users', 'Number of active users')
```

#### 📊 Grafana дашборды

Создайте дашборды для мониторинга:
- **Заказы** — количество, статусы, время обработки
- **Платежи** — успешные, неуспешные, суммы
- **Пользователи** — активные, новые, регистрации
- **Система** — CPU, память, диск, сеть

### 📝 Логирование

#### 🔧 Настройка логирования

```python
import logging
from logging.handlers import RotatingFileHandler

# Настройка логгера
logger = logging.getLogger('cafe_bot')
logger.setLevel(logging.INFO)

# Файловый хендлер
file_handler = RotatingFileHandler(
    'logs/cafe_bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# Формат логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

#### 📊 ELK Stack

1. **Elasticsearch** — хранение логов
2. **Logstash** — обработка логов
3. **Kibana** — визуализация логов

### 🚨 Алерты

#### 📱 Telegram уведомления

```python
async def send_alert(message: str):
    """Отправка алерта в Telegram."""
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🚨 ALERT: {message}"
    )
```

#### 📧 Email уведомления

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject: str, message: str):
    """Отправка алерта по email."""
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'alerts@yourdomain.com'
    msg['To'] = 'admin@yourdomain.com'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('alerts@yourdomain.com', 'password')
    server.send_message(msg)
    server.quit()
```

---

## 🐛 Troubleshooting

### ❌ Проблемы с платежами

#### 💳 Webhook не приходит

**Симптомы**: Платежи проходят, но статус не обновляется

**Диагностика**:
1. Проверьте доступность webhook URL
2. Проверьте SSL сертификат
3. Проверьте логи nginx и приложения

**Решения**:
```bash
# Проверить доступность
curl -I https://yourdomain.com/webhook/yookassa

# Проверить SSL
openssl s_client -connect yourdomain.com:443

# Проверить логи
tail -f /var/log/nginx/error.log
docker-compose logs -f app
```

#### 💰 Платеж не обрабатывается

**Симптомы**: Платеж создан, но не подтверждается

**Диагностика**:
1. Проверьте настройки ЮKassa
2. Проверьте webhook secret
3. Проверьте логи обработки платежей

**Решения**:
```python
# Проверить подпись webhook
def verify_yookassa_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### 🗺️ Проблемы с картами

#### 📍 Яндекс.Карты возвращает ошибку

**Симптомы**: Автоподсказки адресов не работают

**Диагностика**:
1. Проверьте API ключ
2. Проверьте лимиты запросов
3. Проверьте формат запросов

**Решения**:
```bash
# Проверить API ключ
curl "https://geocode-maps.yandex.ru/1.x/?apikey=YOUR_KEY&geocode=Moscow"

# Проверить лимиты в личном кабинете
# https://developer.tech.yandex.ru/
```

### 🍽️ Проблемы с iiko

#### 🔄 iiko не отвечает

**Симптомы**: Синхронизация меню не работает

**Диагностика**:
1. Проверьте подключение к интернету
2. Проверьте настройки API
3. Проверьте статус iiko серверов

**Решения**:
```python
# Проверить подключение
import aiohttp

async def test_iiko_connection():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://api-ru.iiko.services/api/auth/access_token') as response:
                return response.status == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False
```

### 📊 Проблемы с Google Sheets

#### 📈 Google Sheets не обновляется

**Симптомы**: Аналитика не экспортируется

**Диагностика**:
1. Проверьте credentials.json
2. Проверьте права доступа к таблице
3. Проверьте ID таблицы

**Решения**:
```python
# Проверить доступ к таблице
import gspread
from google.oauth2.service_account import Credentials

def test_sheets_access():
    try:
        creds = Credentials.from_service_account_file('credentials.json')
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key('YOUR_SPREADSHEET_ID')
        return True
    except Exception as e:
        print(f"Sheets access error: {e}")
        return False
```

### 🗄️ Проблемы с базой данных

#### 🔌 Ошибки подключения к PostgreSQL

**Симптомы**: Бот не может подключиться к БД

**Диагностика**:
1. Проверьте статус PostgreSQL
2. Проверьте настройки подключения
3. Проверьте права пользователя

**Решения**:
```bash
# Проверить статус PostgreSQL
sudo systemctl status postgresql

# Проверить подключение
psql -h localhost -U cafe_bot_user -d cafe_bot

# Проверить логи
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### 🔄 Проблемы с миграциями

**Симптомы**: Ошибки при применении миграций

**Диагностика**:
1. Проверьте версию Alembic
2. Проверьте файлы миграций
3. Проверьте права доступа к БД

**Решения**:
```bash
# Проверить текущую версию
alembic current

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

### 📱 Проблемы с уведомлениями

#### 🔔 Не приходят уведомления пользователям

**Симптомы**: Пользователи не получают уведомления

**Диагностика**:
1. Проверьте токен бота
2. Проверьте права бота
3. Проверьте блокировки пользователей

**Решения**:
```python
# Проверить токен бота
import asyncio
from aiogram import Bot

async def test_bot_token():
    bot = Bot(token='YOUR_BOT_TOKEN')
    try:
        me = await bot.get_me()
        print(f"Bot info: {me}")
        return True
    except Exception as e:
        print(f"Bot token error: {e}")
        return False
    finally:
        await bot.session.close()
```

#### 📢 Не приходят уведомления в канал админа

**Симптомы**: Админ не получает уведомления о заказах

**Диагностика**:
1. Проверьте ADMIN_CHAT_ID
2. Проверьте права бота в канале
3. Проверьте настройки уведомлений

**Решения**:
```python
# Получить ID чата
async def get_chat_id():
    bot = Bot(token='YOUR_BOT_TOKEN')
    updates = await bot.get_updates()
    for update in updates:
        if update.message:
            print(f"Chat ID: {update.message.chat.id}")
```

---

## 📞 Поддержка

### 🆘 Техническая поддержка

- **📧 Email**: support@example.com
- **📱 Telegram**: @support_bot
- **🌐 Сайт**: https://support.example.com

### 📚 Дополнительные ресурсы

- **📖 Документация API**: https://docs.example.com/api
- **🎥 Видеоуроки**: https://tutorials.example.com
- **💬 Сообщество**: https://community.example.com

### 🔄 Обновления

- **📢 Новости**: Подпишитесь на канал обновлений
- **🐛 Баг-репорты**: Сообщайте об ошибках
- **💡 Предложения**: Предлагайте улучшения

---

*Руководство обновлено: {{ current_date }}*
