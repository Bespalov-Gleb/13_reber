# 🐛 Руководство по решению проблем

## 📋 Содержание

1. [Общие проблемы](#общие-проблемы)
2. [Проблемы с ботом](#проблемы-с-ботом)
3. [Проблемы с базой данных](#проблемы-с-базой-данных)
4. [Проблемы с платежами](#проблемы-с-платежами)
5. [Проблемы с уведомлениями](#проблемы-с-уведомлениями)
6. [Проблемы с интеграциями](#проблемы-с-интеграциями)
7. [Проблемы с производительностью](#проблемы-с-производительностью)
8. [Восстановление после сбоев](#восстановление-после-сбоев)
9. [Диагностические команды](#диагностические-команды)
10. [Контакты поддержки](#контакты-поддержки)

---

## 🔧 Общие проблемы

### ❌ Бот не отвечает

#### 🔍 Симптомы
- Бот не реагирует на команды
- Сообщения не доставляются
- Ошибки в логах

#### 🛠️ Диагностика

```bash
# Проверить статус бота
systemctl status cafe-bot

# Проверить логи
journalctl -u cafe-bot -f

# Проверить подключение к интернету
ping telegram.org

# Проверить токен бота
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

#### ✅ Решения

1. **Проверить токен бота:**
```bash
# В config.env
BOT_TOKEN=your_correct_bot_token_here
```

2. **Перезапустить бота:**
```bash
sudo systemctl restart cafe-bot
```

3. **Проверить права файлов:**
```bash
chmod 600 config.env
chown cafe-bot:cafe-bot config.env
```

4. **Проверить интернет-соединение:**
```bash
# Проверить DNS
nslookup telegram.org

# Проверить прокси/файрвол
curl -I https://api.telegram.org
```

### 🔄 Бот работает нестабильно

#### 🔍 Симптомы
- Периодические сбои
- Медленная работа
- Ошибки в логах

#### 🛠️ Диагностика

```bash
# Проверить использование ресурсов
htop
free -h
df -h

# Проверить логи на ошибки
grep -i error /var/log/cafe-bot.log

# Проверить сетевые соединения
netstat -tlnp | grep :8000
```

#### ✅ Решения

1. **Увеличить лимиты памяти:**
```bash
# В systemd сервисе
[Service]
MemoryLimit=1G
```

2. **Оптимизировать настройки:**
```bash
# В config.env
LOG_LEVEL=WARNING
MAX_WORKERS=4
```

3. **Перезапустить с очисткой:**
```bash
sudo systemctl stop cafe-bot
sudo systemctl start cafe-bot
```

---

## 🤖 Проблемы с ботом

### 📱 Команды не работают

#### 🔍 Симптомы
- Команды не обрабатываются
- Ошибки "Unknown command"
- Бот не реагирует на /start

#### 🛠️ Диагностика

```bash
# Проверить регистрацию команд
grep -r "register" infrastructure/telegram/handlers/

# Проверить логи обработчиков
grep -i "handler" /var/log/cafe-bot.log

# Проверить middleware
grep -i "middleware" /var/log/cafe-bot.log
```

#### ✅ Решения

1. **Проверить регистрацию обработчиков:**
```python
# В bot.py
def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    
    # Регистрация обработчиков
    from infrastructure.telegram.handlers.start_handler import StartHandler
    start_handler = StartHandler()
    dp.include_router(start_handler.router)
    
    return dp
```

2. **Проверить middleware:**
```python
# В bot.py
dp.middleware.setup(DbSessionMiddleware())
dp.middleware.setup(ErrorMiddleware())
```

3. **Перезапустить бота:**
```bash
sudo systemctl restart cafe-bot
```

### 🎯 Callback кнопки не работают

#### 🔍 Симптомы
- Кнопки не реагируют на нажатия
- Ошибки "Callback data invalid"
- Кнопки исчезают

#### 🛠️ Диагностика

```bash
# Проверить логи колбэков
grep -i "callback" /var/log/cafe-bot.log

# Проверить размер callback_data
grep -r "callback_data" infrastructure/telegram/keyboards/
```

#### ✅ Решения

1. **Проверить размер callback_data:**
```python
# Максимум 64 байта
callback_data = f"order_detail:{order_id}"  # OK
callback_data = f"very_long_callback_data_with_many_parameters:{order_id}:{user_id}:{timestamp}"  # TOO LONG
```

2. **Использовать короткие callback_data:**
```python
# Вместо длинных строк используйте коды
callback_data = f"od:{order_id[:8]}"  # order_detail
```

3. **Проверить обработчики колбэков:**
```python
# В handlers
self.router.callback_query.register(
    self.handle_callback,
    F.data.startswith("od:")
)
```

### 📝 Сообщения не отправляются

#### 🔍 Симптомы
- Сообщения не доставляются пользователям
- Ошибки "Chat not found"
- Ошибки "Bot was blocked"

#### 🛠️ Диагностика

```bash
# Проверить логи отправки
grep -i "send_message" /var/log/cafe-bot.log

# Проверить статус пользователей
grep -i "blocked" /var/log/cafe-bot.log
```

#### ✅ Решения

1. **Обработать блокировку бота:**
```python
try:
    await bot.send_message(chat_id, message)
except TelegramBadRequest as e:
    if "bot was blocked" in str(e):
        # Пользователь заблокировал бота
        logger.warning(f"User {chat_id} blocked the bot")
    else:
        raise
```

2. **Проверить права бота:**
```python
# Убедиться, что бот может отправлять сообщения
bot_info = await bot.get_me()
print(f"Bot: {bot_info.username}")
```

3. **Обработать несуществующие чаты:**
```python
try:
    await bot.send_message(chat_id, message)
except TelegramBadRequest as e:
    if "chat not found" in str(e):
        # Чат не найден
        logger.warning(f"Chat {chat_id} not found")
    else:
        raise
```

---

## 🗄️ Проблемы с базой данных

### 🔌 Ошибки подключения

#### 🔍 Симптомы
- "Connection refused"
- "Database not found"
- "Authentication failed"

#### 🛠️ Диагностика

```bash
# Проверить статус PostgreSQL
systemctl status postgresql

# Проверить подключение
psql -h localhost -U cafe_bot_user -d cafe_bot

# Проверить логи PostgreSQL
tail -f /var/log/postgresql/postgresql-14-main.log

# Проверить настройки подключения
grep -r "DATABASE_URL" config.env
```

#### ✅ Решения

1. **Проверить настройки подключения:**
```env
# В config.env
DATABASE_URL=postgresql://cafe_bot_user:password@localhost:5432/cafe_bot
```

2. **Перезапустить PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

3. **Проверить права пользователя:**
```sql
-- В PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE cafe_bot TO cafe_bot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cafe_bot_user;
```

4. **Проверить настройки pg_hba.conf:**
```bash
# В /etc/postgresql/14/main/pg_hba.conf
local   cafe_bot         cafe_bot_user                    md5
host    cafe_bot         cafe_bot_user    127.0.0.1/32   md5
```

### 🔄 Ошибки миграций

#### 🔍 Симптомы
- "Migration failed"
- "Table already exists"
- "Column not found"

#### 🛠️ Диагностика

```bash
# Проверить текущую версию
alembic current

# Проверить историю миграций
alembic history

# Проверить pending миграции
alembic show head
```

#### ✅ Решения

1. **Применить миграции:**
```bash
alembic upgrade head
```

2. **Откатить миграцию:**
```bash
alembic downgrade -1
```

3. **Создать новую миграцию:**
```bash
alembic revision --autogenerate -m "Fix migration"
alembic upgrade head
```

4. **Сбросить миграции (ОСТОРОЖНО!):**
```bash
# Только для разработки!
alembic downgrade base
alembic upgrade head
```

### 📊 Медленные запросы

#### 🔍 Симптомы
- Медленная работа бота
- Таймауты запросов
- Высокая нагрузка на БД

#### 🛠️ Диагностика

```bash
# Проверить активные запросы
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Проверить медленные запросы
sudo -u postgres psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Проверить размер БД
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('cafe_bot'));"
```

#### ✅ Решения

1. **Добавить индексы:**
```sql
-- Создать индексы для часто используемых полей
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

2. **Оптимизировать запросы:**
```python
# Использовать select_related для связанных объектов
orders = await session.execute(
    select(OrderModel)
    .options(selectinload(OrderModel.items))
    .where(OrderModel.user_id == user_id)
)
```

3. **Настроить connection pooling:**
```python
# В database/connection.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

---

## 💳 Проблемы с платежами

### 🔗 Webhook не приходит

#### 🔍 Симптомы
- Платежи проходят, но статус не обновляется
- Ошибки "Webhook timeout"
- Платежи висят в статусе "pending"

#### 🛠️ Диагностика

```bash
# Проверить доступность webhook
curl -I https://yourdomain.com/webhook/yookassa

# Проверить SSL сертификат
openssl s_client -connect yourdomain.com:443

# Проверить логи nginx
tail -f /var/log/nginx/error.log

# Проверить логи приложения
grep -i "webhook" /var/log/cafe-bot.log
```

#### ✅ Решения

1. **Проверить настройки webhook в ЮKassa:**
```bash
# URL должен быть доступен
https://yourdomain.com/webhook/yookassa

# Проверить SSL сертификат
curl -k https://yourdomain.com/webhook/yookassa
```

2. **Проверить nginx конфигурацию:**
```nginx
location /webhook/yookassa {
    proxy_pass http://localhost:8000/webhook/yookassa;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

3. **Проверить обработчик webhook:**
```python
# В webhook_handler.py
async def handle_yookassa_webhook(request):
    try:
        # Обработка webhook
        data = await request.json()
        await process_payment(data)
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(status=500)
```

### 💰 Платеж не обрабатывается

#### 🔍 Симптомы
- Платеж создан, но не подтверждается
- Ошибки "Invalid signature"
- Платеж отклонен

#### 🛠️ Диагностика

```bash
# Проверить настройки ЮKassa
grep -r "YOOKASSA" config.env

# Проверить логи платежей
grep -i "payment" /var/log/cafe-bot.log

# Проверить подпись webhook
grep -i "signature" /var/log/cafe-bot.log
```

#### ✅ Решения

1. **Проверить настройки ЮKassa:**
```env
# В config.env
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_SECRET_KEY=your_secret_key_here
YOOKASSA_WEBHOOK_SECRET=your_webhook_secret_here
```

2. **Проверить подпись webhook:**
```python
def verify_yookassa_signature(payload, signature, secret):
    """Проверка подписи webhook."""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

3. **Проверить обработку платежей:**
```python
async def process_payment(payment_data):
    """Обработка платежа."""
    payment_id = payment_data.get("object", {}).get("id")
    status = payment_data.get("object", {}).get("status")
    
    if status == "succeeded":
        await update_order_payment_status(payment_id, "paid")
    elif status == "canceled":
        await update_order_payment_status(payment_id, "failed")
```

### 🔄 Возврат платежа

#### 🔍 Симптомы
- Невозможно вернуть платеж
- Ошибки "Refund failed"
- Платеж не возвращается

#### 🛠️ Диагностика

```bash
# Проверить логи возвратов
grep -i "refund" /var/log/cafe-bot.log

# Проверить настройки возвратов в ЮKassa
# В личном кабинете ЮKassa
```

#### ✅ Решения

1. **Проверить права на возврат:**
```python
async def refund_payment(payment_id: str, amount: int):
    """Возврат платежа."""
    try:
        refund = await yookassa_client.refund_payment(
            payment_id=payment_id,
            amount={"value": str(amount / 100), "currency": "RUB"}
        )
        return refund
    except Exception as e:
        logger.error(f"Refund failed: {e}")
        raise
```

2. **Проверить статус платежа:**
```python
# Возврат возможен только для успешных платежей
if payment.status != "succeeded":
    raise ValueError("Cannot refund non-succeeded payment")
```

---

## 📱 Проблемы с уведомлениями

### 🔔 Уведомления не приходят

#### 🔍 Симптомы
- Админ не получает уведомления о заказах
- Пользователи не получают уведомления
- Ошибки "Chat not found"

#### 🛠️ Диагностика

```bash
# Проверить настройки уведомлений
grep -r "ADMIN_CHAT_ID" config.env

# Проверить логи уведомлений
grep -i "notification" /var/log/cafe-bot.log

# Проверить права бота в чате
```

#### ✅ Решения

1. **Проверить ADMIN_CHAT_ID:**
```env
# В config.env
ADMIN_CHAT_ID=-1001234567890  # ID чата/канала
```

2. **Проверить права бота в чате:**
```python
# Бот должен быть администратором чата
# Иметь права на отправку сообщений
```

3. **Проверить обработчик уведомлений:**
```python
async def send_admin_notification(message: str):
    """Отправка уведомления админу."""
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        logger.error(f"Failed to send admin notification: {e}")
```

### 📢 Массовая рассылка не работает

#### 🔍 Симптомы
- Рассылка не отправляется
- Ошибки "Too many requests"
- Блокировка бота

#### 🛠️ Диагностика

```bash
# Проверить логи рассылки
grep -i "broadcast" /var/log/cafe-bot.log

# Проверить лимиты Telegram
# 30 сообщений в секунду
```

#### ✅ Решения

1. **Добавить задержки между сообщениями:**
```python
async def send_broadcast(users: List[str], message: str):
    """Массовая рассылка с задержками."""
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=message)
            await asyncio.sleep(0.1)  # 100ms задержка
        except TelegramBadRequest as e:
            logger.warning(f"Failed to send to {user_id}: {e}")
```

2. **Использовать очередь для рассылки:**
```python
import asyncio
from asyncio import Queue

class BroadcastQueue:
    """Очередь для массовой рассылки."""
    
    def __init__(self):
        self.queue = Queue()
        self.running = False
    
    async def start(self):
        """Запуск обработки очереди."""
        self.running = True
        while self.running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self._process_task(task)
            except asyncio.TimeoutError:
                continue
    
    async def _process_task(self, task):
        """Обработка задачи рассылки."""
        await asyncio.sleep(0.1)  # Задержка
        await task()
```

---

## 🔌 Проблемы с интеграциями

### 🗺️ Яндекс.Карты не работают

#### 🔍 Симптомы
- Автоподсказки адресов не работают
- Ошибки "API key invalid"
- Геокодирование не работает

#### 🛠️ Диагностика

```bash
# Проверить API ключ
curl "https://geocode-maps.yandex.ru/1.x/?apikey=YOUR_KEY&geocode=Moscow"

# Проверить лимиты запросов
# В личном кабинете Яндекс.Разработчика

# Проверить настройки
grep -r "YANDEX_MAPS" config.env
```

#### ✅ Решения

1. **Проверить API ключ:**
```env
# В config.env
YANDEX_MAPS_API_KEY=your_valid_api_key_here
```

2. **Проверить лимиты запросов:**
```python
# Добавить кэширование для уменьшения запросов
@lru_cache(maxsize=1000)
async def geocode_address(address: str) -> dict:
    """Геокодирование с кэшированием."""
    # Запрос к API
    pass
```

3. **Обработать ошибки API:**
```python
async def get_address_suggestions(query: str) -> List[str]:
    """Получение подсказок адресов."""
    try:
        response = await yandex_maps_api.suggest(query)
        return response.get("suggestions", [])
    except Exception as e:
        logger.error(f"Yandex Maps API error: {e}")
        return []  # Возвращаем пустой список при ошибке
```

### 🍽️ iiko не синхронизируется

#### 🔍 Симптомы
- Меню не обновляется из iiko
- Ошибки "Authentication failed"
- Заказы не отправляются в iiko

#### 🛠️ Диагностика

```bash
# Проверить настройки iiko
grep -r "IIKO" config.env

# Проверить логи iiko
grep -i "iiko" /var/log/cafe-bot.log

# Проверить подключение к iiko
curl -X POST https://api-ru.iiko.services/api/1/access_token \
  -H "Content-Type: application/json" \
  -d '{"apiLogin":"YOUR_API_LOGIN"}'
```

#### ✅ Решения

1. **Проверить настройки iiko:**
```env
# В config.env
IIKO_API_URL=https://api-ru.iiko.services
IIKO_API_LOGIN=your_login_here
IIKO_ORGANIZATION_ID=your_org_id_here
```

2. **Проверить аутентификацию:**
```python
async def test_iiko_connection():
    """Тест подключения к iiko."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{IIKO_API_URL}/api/1/access_token",
                json={"apiLogin": IIKO_API_LOGIN}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error(f"iiko auth failed: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"iiko connection error: {e}")
        return False
```

4. **Проверить обязательные справочники для `deliveries/create`:**
```python
# Нельзя отправлять заказ без валидных ID из iiko:
# - orderTypeId (из /api/1/deliveries/order_types)
# - paymentTypeId (из /api/1/payment_types)
# - terminalGroupId (из /api/1/terminal_groups)
#
# Также после /api/1/deliveries/create проверяйте статус
# через /api/1/commands/status по correlationId.
```

3. **Добавить fallback на локальное меню:**
```python
async def sync_menu_from_iiko():
    """Синхронизация меню с fallback."""
    try:
        # Попытка синхронизации с iiko
        await iiko_sync_service.sync_menu()
    except Exception as e:
        logger.warning(f"iiko sync failed, using local menu: {e}")
        # Используем локальное меню
        pass
```

### 📊 Google Sheets не обновляется

#### 🔍 Симптомы
- Аналитика не экспортируется
- Ошибки "Access denied"
- Таблица не обновляется

#### 🛠️ Диагностика

```bash
# Проверить credentials.json
ls -la credentials.json

# Проверить права доступа к таблице
# В Google Sheets

# Проверить настройки
grep -r "GOOGLE_SHEETS" config.env
```

#### ✅ Решения

1. **Проверить credentials.json:**
```bash
# Файл должен существовать и быть доступен
chmod 600 credentials.json
chown cafe-bot:cafe-bot credentials.json
```

2. **Проверить права доступа к таблице:**
```python
# Service Account должен иметь доступ к таблице
# В Google Sheets: Поделиться → Добавить Service Account email
```

3. **Проверить ID таблицы:**
```env
# В config.env
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

4. **Обработать ошибки доступа:**
```python
async def log_to_sheets(data: dict):
    """Логирование в Google Sheets с обработкой ошибок."""
    try:
        await google_sheets.log_data(data)
    except Exception as e:
        logger.error(f"Google Sheets error: {e}")
        # Можно сохранить в локальный файл как fallback
        await save_to_local_file(data)
```

---

## ⚡ Проблемы с производительностью

### 🐌 Медленная работа бота

#### 🔍 Симптомы
- Медленные ответы на команды
- Таймауты запросов
- Высокая нагрузка на сервер

#### 🛠️ Диагностика

```bash
# Проверить использование ресурсов
htop
free -h
df -h

# Проверить медленные запросы
grep -i "slow" /var/log/cafe-bot.log

# Проверить количество соединений
netstat -an | grep :8000 | wc -l
```

#### ✅ Решения

1. **Оптимизировать запросы к БД:**
```python
# Использовать select_related для связанных объектов
orders = await session.execute(
    select(OrderModel)
    .options(selectinload(OrderModel.items))
    .where(OrderModel.user_id == user_id)
)
```

2. **Добавить кэширование:**
```python
# Кэширование часто используемых данных
@lru_cache(maxsize=1000)
async def get_menu_categories():
    """Получение категорий меню с кэшированием."""
    return await menu_repository.get_categories()
```

3. **Оптимизировать настройки:**
```python
# В config.env
MAX_WORKERS=4
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

### 💾 Высокое использование памяти

#### 🔍 Симптомы
- Бот потребляет много памяти
- Ошибки "Out of memory"
- Медленная работа системы

#### 🛠️ Диагностика

```bash
# Проверить использование памяти
free -h
ps aux --sort=-%mem | head -10

# Проверить утечки памяти
valgrind --tool=memcheck python -m app.main
```

#### ✅ Решения

1. **Оптимизировать загрузку данных:**
```python
# Загружать только необходимые данные
async def get_orders_list(user_id: str, limit: int = 10):
    """Получение списка заказов с лимитом."""
    return await order_repository.list_orders(
        filters=OrderFilters(user_id=user_id, limit=limit)
    )
```

2. **Очищать кэш:**
```python
# Периодическая очистка кэша
import gc

async def cleanup_memory():
    """Очистка памяти."""
    gc.collect()
    # Очистка кэша
    cache.clear()
```

3. **Настроить лимиты памяти:**
```bash
# В systemd сервисе
[Service]
MemoryLimit=1G
MemoryHigh=800M
```

### 🔄 Медленные фоновые задачи

#### 🔍 Симптомы
- Синхронизация с iiko медленная
- Backup занимает много времени
- Очередь задач растет

#### 🛠️ Диагностика

```bash
# Проверить фоновые задачи
ps aux | grep -i "background"

# Проверить логи фоновых задач
grep -i "background" /var/log/cafe-bot.log

# Проверить очередь задач
```

#### ✅ Решения

1. **Оптимизировать фоновые задачи:**
```python
# Использовать asyncio для параллельной обработки
async def sync_menu_batch(menu_items: List[MenuItem]):
    """Пакетная синхронизация меню."""
    tasks = []
    for item in menu_items:
        task = asyncio.create_task(sync_menu_item(item))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
```

2. **Добавить мониторинг задач:**
```python
# Мониторинг выполнения задач
import time

async def monitored_task(task_func, *args, **kwargs):
    """Выполнение задачи с мониторингом."""
    start_time = time.time()
    try:
        result = await task_func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"Task {task_func.__name__} completed in {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Task {task_func.__name__} failed after {duration:.2f}s: {e}")
        raise
```

---

## 🔄 Восстановление после сбоев

### 💾 Восстановление из backup

#### 📥 Восстановление базы данных

```bash
# Остановить приложение
sudo systemctl stop cafe-bot

# Восстановить базу данных
gunzip -c /opt/cafe-bot/backups/cafe_bot_20240101_020000.sql.gz | \
psql -h localhost -U cafe_bot_user -d cafe_bot

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

### 🔄 Откат к предыдущей версии

#### 📦 Откат кода

```bash
# Перейти в директорию проекта
cd /opt/cafe-bot

# Откатить к предыдущему коммиту
git log --oneline -10  # Посмотреть историю
git reset --hard HEAD~1  # Откатить на 1 коммит назад

# Перезапустить приложение
sudo systemctl restart cafe-bot
```

#### 🐳 Откат Docker

```bash
# Откатить к предыдущему образу
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 🔧 Восстановление конфигурации

#### ⚙️ Восстановление config.env

```bash
# Создать новый config.env из backup
cp /opt/cafe-bot/backups/config.env.backup /opt/cafe-bot/config.env

# Установить права
chmod 600 /opt/cafe-bot/config.env
chown cafe-bot:cafe-bot /opt/cafe-bot/config.env

# Перезапустить приложение
sudo systemctl restart cafe-bot
```

---

## 🔍 Диагностические команды

### 📊 Системная информация

```bash
# Информация о системе
uname -a
lsb_release -a
cat /proc/version

# Использование ресурсов
htop
free -h
df -h
iostat -x 1

# Сетевые соединения
netstat -tlnp
ss -tlnp
```

### 🗄️ База данных

```bash
# Статус PostgreSQL
systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# Размер БД
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('cafe_bot'));"

# Активные соединения
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Медленные запросы
sudo -u postgres psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### 🤖 Приложение

```bash
# Статус сервисов
systemctl status cafe-bot
systemctl status nginx
systemctl status redis

# Логи приложения
journalctl -u cafe-bot -f
tail -f /var/log/cafe-bot.log

# Логи nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Логи PostgreSQL
tail -f /var/log/postgresql/postgresql-14-main.log
```

### 🌐 Сеть

```bash
# Проверка подключения
ping telegram.org
curl -I https://api.telegram.org

# Проверка портов
nmap localhost
telnet localhost 8000

# Проверка DNS
nslookup telegram.org
dig telegram.org
```

### 🔍 Процессы

```bash
# Процессы приложения
ps aux | grep cafe-bot
ps aux | grep python

# Дерево процессов
pstree -p

# Использование файлов
lsof -p $(pgrep cafe-bot)
```

---

## 📞 Контакты поддержки

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
