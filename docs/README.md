# 🍽️ Telegram Bot для Кафе

Полнофункциональная система управления заказами для ресторанов и кафе через Telegram.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://aiogram.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Возможности

### 👥 Для клиентов
- 📱 Удобный интерфейс через Telegram
- 🍽️ Просмотр меню с фотографиями и описаниями
- 🛒 Корзина покупок с возможностью редактирования
- 📍 Выбор способа получения (доставка/самовывоз)
- 🗺️ Автоподсказки адресов через Яндекс.Карты
- 💳 Онлайн-оплата через ЮKassa
- 🪑 Бронирование столиков
- ⭐ Система отзывов
- 🎁 Промокоды и акции

### 👨‍💼 Для администраторов
- 📊 Полная админ-панель
- 📋 Управление заказами в реальном времени
- 🍽️ Управление меню и категориями
- 👥 Управление пользователями
- 💰 Управление платежами
- 📢 Система уведомлений
- 📈 Аналитика и статистика
- 🚚 Управление курьерами
- 🪑 Управление бронированиями

### 🚚 Для курьеров
- 📦 Интерфейс для доставки
- 🗺️ Навигация к клиентам
- 📞 Связь с клиентами
- ✅ Отметка о доставке

## 🏗️ Архитектура

Проект построен на принципах **Clean Architecture** и **Domain-Driven Design**:

- **🌐 Infrastructure Layer** — Telegram Bot, PostgreSQL, внешние API
- **🔧 Application Layer** — обработчики, сервисы, события
- **💎 Domain Layer** — сущности, бизнес-логика, репозитории

### Технологический стек

- **Python 3.10+** — основной язык
- **aiogram 3.x** — асинхронный Telegram Bot API
- **SQLAlchemy 2.x** — ORM для работы с БД
- **PostgreSQL** — основная база данных
- **Redis** — кэширование и сессии
- **Pydantic** — валидация данных
- **Docker** — контейнеризация

## 🚀 Быстрый старт

### 📋 Требования

- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (опционально)
- Docker & Docker Compose (для развертывания)

### 🐳 Docker (рекомендуется)

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/cafe-bot.git
cd cafe-bot

# Настройка конфигурации
cp config.env.example config.env
# Отредактируйте config.env с вашими настройками

# Запуск через Docker Compose
docker-compose up -d

# Применение миграций
docker-compose exec app alembic upgrade head
```

### 🔧 Локальная установка

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/cafe-bot.git
cd cafe-bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
createdb cafe_bot

# Настройка конфигурации
cp config.env.example config.env
# Отредактируйте config.env

# Применение миграций
alembic upgrade head

# Запуск бота
python -m app.main
```

## ⚙️ Конфигурация

Основные настройки в `config.env`:

```env
# Основные настройки
BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_telegram_id_here
ADMIN_CHAT_ID=your_admin_chat_id_here

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/cafe_bot

# Платежные системы
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_SECRET_KEY=your_secret_key_here

# Яндекс.Карты
YANDEX_MAPS_API_KEY=your_api_key_here

# iiko CRM
IIKO_API_URL=https://api-ru.iiko.services
IIKO_API_LOGIN=your_api_login_here
```

## 📁 Структура проекта

```
cafe_bot/
├── 📁 app/                          # Точка входа приложения
├── 📁 domain/                       # Доменный слой
│   ├── 📁 entities/                 # Сущности
│   ├── 📁 services/                 # Доменные сервисы
│   ├── 📁 repositories/             # Интерфейсы репозиториев
│   ├── 📁 value_objects/            # Объекты-значения
│   ├── 📁 events/                   # События
│   └── 📁 exceptions/               # Исключения
├── 📁 infrastructure/               # Слой инфраструктуры
│   ├── 📁 telegram/                 # Telegram Bot
│   ├── 📁 database/                 # База данных
│   ├── 📁 external/                 # Внешние API
│   └── 📁 events/                   # Обработчики событий
├── 📁 shared/                       # Общие компоненты
├── 📁 tests/                        # Тесты
├── 📁 docs/                         # Документация
└── 📁 docker/                       # Docker конфигурация
```

## 📖 Документация

- **[📚 Полная документация](docs/README.md)** — обзор всех возможностей
- **[👨‍💼 Руководство администратора](admin_manual.md)** — управление ботом
- **[🔌 Руководство по интеграциям](integration_guide.md)** — настройка внешних сервисов
- **[🚀 Руководство по развертыванию](deployment_guide.md)** — развертывание в production
- **[👨‍💻 Руководство разработчика](developer_guide.md)** — архитектура и разработка
- **[🐛 Решение проблем](troubleshooting.md)** — частые проблемы и их решения

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=. --cov-report=html

# Запуск конкретного теста
pytest tests/unit/test_order_service.py
```

## 🔧 Разработка

### 📝 Стиль кода

```bash
# Форматирование
black .
isort .

# Линтинг
flake8 .
mypy .
```

### 🔄 CI/CD

- **GitHub Actions** — автоматические тесты
- **Docker Hub** — автоматическая сборка образов
- **Webhook** — автоматическое развертывание

## 🌐 Развертывание

### ☁️ Cloud платформы

- **DigitalOcean** — Droplet 4GB/2CPU
- **AWS** — t3.medium EC2
- **Google Cloud** — e2-standard-2
- **Vultr** — High Frequency 4GB

### 🐳 Docker Production

```bash
# Сборка и запуск
docker-compose -f docker/docker-compose.prod.yml up -d

# Логи
docker-compose logs -f app

# Обновление
docker-compose pull
docker-compose up -d
```

## 📊 Мониторинг

- **Prometheus** — метрики
- **Grafana** — дашборды
- **ELK Stack** — логи
- **Uptime Robot** — мониторинг доступности

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- **aiogram** — фреймворк для Telegram Bot API
- **SQLAlchemy** — ORM для работы с базой данных
- **PostgreSQL** — надежная база данных
- **Docker** — контейнеризация приложения

## 📞 Поддержка

- **📧 Email**: support@example.com
- **📱 Telegram**: @support_bot
- **🌐 Сайт**: https://support.example.com

---

*Сделано с ❤️ для ресторанов и кафе*