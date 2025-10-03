# Cafe Bot - Telegram Bot for Cafe Management

Современный Telegram-бот для управления кафе с полным функционалом заказов, оплаты и администрирования.

## 🚀 Возможности

- 📖 **Меню с категориями** - структурированное меню с фото и описаниями
- 🛒 **Корзина** - добавление товаров с количеством и комментариями
- 🚚 **Заказы** - оформление заказов с доставкой и самовывозом
- 💳 **Оплата** - интеграция с ЮKassa, CloudPayments, Stripe
- 📍 **Геолокация** - проверка зоны доставки через Яндекс.Карты
- 🔔 **Уведомления** - автоматические уведомления о статусе заказа
- 👨‍💼 **Админ-панель** - управление заказами и меню
- 📊 **Аналитика** - отчеты и статистика

## 🏗️ Архитектура

Проект построен на принципах **Clean Architecture** и **Domain-Driven Design**:

- **Domain Layer** - бизнес-логика и правила
- **Infrastructure Layer** - внешние интеграции и БД
- **Application Layer** - use cases и координация
- **Shared Layer** - общие компоненты

### Технологический стек

- **Python 3.11+** - основной язык
- **aiogram 3.x** - асинхронный Telegram Bot API
- **SQLAlchemy 2.x** - ORM для работы с БД
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и сессии
- **Pydantic** - валидация данных
- **Docker** - контейнеризация

## 🛠️ Установка и запуск

### Требования

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (опционально)

### Локальная установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd cafe_bot
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка переменных окружения**
```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

5. **Настройка базы данных**
```bash
# Создайте базу данных PostgreSQL
createdb cafe_bot

# Запустите миграции
alembic upgrade head
```

6. **Запуск бота**
```bash
python -m app.main
```

### Docker

```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
```

## ⚙️ Конфигурация

Основные настройки в файле `.env`:

### Bot Configuration
- `BOT_TOKEN` - токен Telegram бота
- `BOT_WEBHOOK_URL` - URL для webhook (для продакшена)

### Database
- `DATABASE_URL` - строка подключения к PostgreSQL
- `REDIS_URL` - строка подключения к Redis

### Payment Systems
- `YOOKASSA_SHOP_ID` - ID магазина в ЮKassa
- `YOOKASSA_SECRET_KEY` - секретный ключ ЮKassa

### Maps
- `YANDEX_MAPS_API_KEY` - API ключ Яндекс.Карт

### CRM
- `IIKO_API_LOGIN` - логин для iiko API
- `IIKO_API_PASSWORD` - пароль для iiko API

## 📁 Структура проекта

```
cafe_bot/
├── app/                    # Точка входа приложения
├── domain/                 # Доменный слой
│   ├── entities/          # Доменные сущности
│   ├── value_objects/     # Объекты-значения
│   ├── repositories/      # Интерфейсы репозиториев
│   ├── services/          # Доменные сервисы
│   ├── events/            # Доменные события
│   └── exceptions/        # Доменные исключения
├── infrastructure/        # Инфраструктурный слой
│   ├── database/         # Работа с БД
│   ├── telegram/         # Telegram интеграция
│   ├── external/         # Внешние сервисы
│   └── events/           # Обработчики событий
├── application/          # Слой приложения
│   ├── commands/         # Команды (CQRS)
│   ├── queries/          # Запросы (CQRS)
│   └── handlers/         # Обработчики
├── shared/               # Общие компоненты
├── tests/                # Тесты
└── migrations/           # Миграции БД
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск только юнит тестов
pytest tests/unit/

# Запуск с покрытием
pytest --cov=cafe_bot

# Запуск интеграционных тестов
pytest tests/integration/
```

## 📊 Мониторинг

- **Prometheus** - метрики приложения
- **Grafana** - дашборды и визуализация
- **Structured Logging** - структурированные логи

## 🔧 Разработка

### Code Style

```bash
# Форматирование кода
black cafe_bot/

# Сортировка импортов
isort cafe_bot/

# Проверка стиля
flake8 cafe_bot/

# Проверка типов
mypy cafe_bot/
```

### Миграции БД

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 📚 Документация

- [API Documentation](docs/api.md)
- [Admin Guide](docs/admin.md)
- [Integration Guide](docs/integrations.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [Issues](https://github.com/your-repo/issues)
2. Создайте новый Issue с подробным описанием
3. Свяжитесь с командой разработки

---

**Сделано с ❤️ для кафе**