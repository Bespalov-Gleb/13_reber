# 👨‍💻 Руководство разработчика

## 📋 Содержание

1. [Архитектура проекта](#архитектура-проекта)
2. [Принципы разработки](#принципы-разработки)
3. [Структура кода](#структура-кода)
4. [Добавление новых функций](#добавление-новых-функций)
5. [Тестирование](#тестирование)
6. [Стиль кода](#стиль-кода)
7. [CI/CD](#cicd)
8. [Отладка](#отладка)
9. [Производительность](#производительность)
10. [Безопасность](#безопасность)

---

## 🏗️ Архитектура проекта

### 📐 Clean Architecture

Проект построен на принципах **Clean Architecture** с четким разделением на слои:

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 Infrastructure Layer                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Telegram  │ │  Database   │ │  External   │           │
│  │   Bot API   │ │ PostgreSQL  │ │   APIs      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    🔧 Application Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Handlers   │ │   Services  │ │   Events    │           │
│  │             │ │             │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      💎 Domain Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Entities   │ │  Services   │ │ Value Objects│           │
│  │             │ │             │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 Поток данных

1. **Входящий запрос** → Telegram Bot API
2. **Middleware** → Аутентификация, логирование, сессии
3. **Handler** → Обработка команды/колбэка
4. **Service** → Бизнес-логика
5. **Repository** → Работа с базой данных
6. **Response** → Форматирование и отправка ответа

### 🎯 Принципы архитектуры

#### 🔒 Dependency Inversion
- Высокоуровневые модули не зависят от низкоуровневых
- Оба зависят от абстракций
- Абстракции не зависят от деталей

#### 🧩 Single Responsibility
- Каждый класс имеет одну причину для изменения
- Четкое разделение ответственности между компонентами

#### 🔄 Open/Closed
- Открыт для расширения
- Закрыт для модификации

#### 🔗 Interface Segregation
- Клиенты не должны зависеть от интерфейсов, которые они не используют

#### 🔄 Liskov Substitution
- Объекты производных классов должны заменять объекты базовых классов

---

## 🎯 Принципы разработки

### 🏛️ Domain-Driven Design (DDD)

#### 💎 Domain Layer (Доменный слой)

**Entities** — основные бизнес-объекты:
```python
# domain/entities/order.py
@dataclass
class Order:
    """Заказ - основная сущность бизнеса."""
    order_id: str
    user_id: str
    items: List[OrderItem]
    status: OrderStatus
    total: int
    created_at: datetime
```

**Value Objects** — неизменяемые объекты:
```python
# domain/value_objects/money.py
@dataclass(frozen=True)
class Money:
    """Деньги - объект-значение."""
    amount: int  # в копейках
    currency: str = "RUB"
    
    def to_rubles(self) -> float:
        return self.amount / 100
```

**Domain Services** — бизнес-логика:
```python
# domain/services/order_service.py
class OrderService:
    """Сервис для работы с заказами."""
    
    async def create_order(self, user_id: str, cart: Cart) -> Order:
        """Создание заказа с бизнес-правилами."""
        # Валидация
        if not cart.items:
            raise EmptyCartError()
        
        # Создание заказа
        order = Order(...)
        
        # Применение бизнес-правил
        await self._apply_discounts(order)
        await self._calculate_delivery(order)
        
        return order
```

#### 🔧 Application Layer (Слой приложения)

**Handlers** — обработчики команд:
```python
# infrastructure/telegram/handlers/order_handler.py
class OrderHandler(BaseHandler):
    """Обработчик команд заказов."""
    
    async def handle_order_command(self, message: Message) -> None:
        """Обработка команды /order."""
        user_id = message.from_user.id
        
        # Получение корзины
        cart_service = await get_cart_service()
        cart = await cart_service.get_cart(user_id)
        
        # Создание заказа
        order_service = await get_order_service()
        order = await order_service.create_order(user_id, cart)
        
        # Отправка ответа
        await message.answer("Заказ создан!")
```

**Services** — сервисы приложения:
```python
# domain/services/notification_service.py
class NotificationService:
    """Сервис уведомлений."""
    
    async def send_order_notification(self, order: Order) -> None:
        """Отправка уведомления о заказе."""
        # Форматирование сообщения
        message = self._format_order_message(order)
        
        # Отправка админу
        await self._send_to_admin(message)
        
        # Отправка клиенту
        await self._send_to_customer(order.user_id, message)
```

#### 🌐 Infrastructure Layer (Слой инфраструктуры)

**Repositories** — работа с данными:
```python
# infrastructure/database/repositories/order_repository_impl.py
class OrderRepositoryImpl(OrderRepository):
    """Реализация репозитория заказов."""
    
    async def create(self, order: Order) -> Order:
        """Создание заказа в БД."""
        db_order = OrderModel(
            id=order.order_id,
            user_id=order.user_id,
            status=order.status.value,
            total=order.total
        )
        
        self.session.add(db_order)
        await self.session.commit()
        
        return self._model_to_entity(db_order)
```

**External APIs** — внешние сервисы:
```python
# infrastructure/external/payment/yookassa_payment.py
class YooKassaPaymentIntegration:
    """Интеграция с ЮKassa."""
    
    async def create_payment(self, order: Order) -> Payment:
        """Создание платежа в ЮKassa."""
        payload = {
            "amount": {"value": str(order.total / 100), "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": self.return_url},
            "description": f"Заказ #{order.order_id}"
        }
        
        response = await self._make_request("POST", "/payments", payload)
        return Payment(payment_id=response["id"], ...)
```

### 🔄 Event-Driven Architecture

#### 📢 События

```python
# domain/events/order_created.py
@dataclass
class OrderCreatedEvent:
    """Событие создания заказа."""
    order: Order
    timestamp: datetime = field(default_factory=datetime.now)
```

#### 🎯 Обработчики событий

```python
# infrastructure/events/order_event_handlers.py
class OrderEventHandlers:
    """Обработчики событий заказов."""
    
    async def handle_order_created(self, event: OrderCreatedEvent) -> None:
        """Обработка создания заказа."""
        # Отправка уведомления
        notification_service = await get_notification_service()
        await notification_service.send_order_notification(event.order)
        
        # Отправка в iiko
        iiko_service = await get_iiko_sync_service()
        await iiko_service.send_order_to_iiko(event.order)
```

---

## 📁 Структура кода

### 🗂️ Организация файлов

```
cafe_bot/
├── 📁 app/                          # Точка входа
│   ├── main.py                      # Запуск приложения
│   ├── config.py                    # Конфигурация
│   ├── dependencies.py              # DI контейнер
│   └── background_tasks.py          # Фоновые задачи
│
├── 📁 domain/                       # Доменный слой
│   ├── 📁 entities/                 # Сущности
│   ├── 📁 services/                 # Доменные сервисы
│   ├── 📁 repositories/             # Интерфейсы репозиториев
│   ├── 📁 value_objects/            # Объекты-значения
│   ├── 📁 events/                   # События
│   └── 📁 exceptions/               # Исключения
│
├── 📁 infrastructure/               # Слой инфраструктуры
│   ├── 📁 telegram/                 # Telegram Bot
│   ├── 📁 database/                 # База данных
│   ├── 📁 external/                 # Внешние API
│   ├── 📁 events/                   # Обработчики событий
│   └── 📁 logging/                  # Логирование
│
├── 📁 shared/                       # Общие компоненты
│   ├── 📁 constants/                # Константы
│   ├── 📁 types/                    # Типы данных
│   └── 📁 utils/                    # Утилиты
│
└── 📁 tests/                        # Тесты
    ├── 📁 unit/                     # Юнит-тесты
    ├── 📁 integration/              # Интеграционные тесты
    └── 📁 fixtures/                 # Тестовые данные
```

### 📝 Соглашения по именованию

#### 🏷️ Файлы и модули
- **snake_case** для файлов: `order_handler.py`
- **snake_case** для модулей: `order_handler`
- **PascalCase** для классов: `OrderHandler`

#### 🔤 Переменные и функции
- **snake_case** для переменных: `user_id`, `order_total`
- **snake_case** для функций: `create_order()`, `get_user_by_id()`
- **UPPER_CASE** для констант: `MAX_ORDER_AMOUNT`

#### 🏗️ Классы и интерфейсы
- **PascalCase** для классов: `OrderService`, `UserRepository`
- **Interface** суффикс для интерфейсов: `OrderRepository`
- **Impl** суффикс для реализаций: `OrderRepositoryImpl`

### 📋 Структура классов

#### 🏗️ Базовые классы

```python
# infrastructure/telegram/handlers/base_handler.py
class BaseHandler:
    """Базовый класс для всех обработчиков."""
    
    def __init__(self):
        self.router = Router()
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков. Переопределить в наследниках."""
        pass
    
    async def safe_edit_message(self, message: Message, **kwargs) -> None:
        """Безопасное редактирование сообщения."""
        try:
            await message.edit_text(**kwargs)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass  # Игнорируем если сообщение не изменилось
            else:
                raise
```

#### 🎯 Обработчики

```python
# infrastructure/telegram/handlers/order_handler.py
class OrderHandler(BaseHandler):
    """Обработчик заказов."""
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков заказов."""
        self.router.message.register(
            self.handle_order_command, 
            F.text == "/order"
        )
        self.router.callback_query.register(
            self.handle_order_callback,
            F.data.startswith("order:")
        )
    
    async def handle_order_command(self, message: Message) -> None:
        """Обработка команды /order."""
        # Логика обработки
        pass
    
    async def handle_order_callback(self, callback: CallbackQuery) -> None:
        """Обработка колбэков заказов."""
        # Логика обработки
        pass
```

#### 🔧 Сервисы

```python
# domain/services/order_service.py
class OrderService:
    """Сервис для работы с заказами."""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    async def create_order(self, user_id: str, cart: Cart) -> Order:
        """Создание заказа."""
        # Валидация
        if not cart.items:
            raise EmptyCartError("Корзина пуста")
        
        # Создание заказа
        order = Order(
            order_id=generate_id(),
            user_id=user_id,
            items=cart.items,
            total=cart.total_price,
            status=OrderStatus.PENDING
        )
        
        # Сохранение
        return await self.order_repository.create(order)
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """Обновление статуса заказа."""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Заказ {order_id} не найден")
        
        order.status = status
        return await self.order_repository.update(order)
```

#### 🗄️ Репозитории

```python
# domain/repositories/order_repository.py
class OrderRepository(ABC):
    """Интерфейс репозитория заказов."""
    
    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Создание заказа."""
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Получение заказа по ID."""
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Обновление заказа."""
        pass
    
    @abstractmethod
    async def list_orders(self, filters: OrderFilters) -> List[Order]:
        """Список заказов с фильтрами."""
        pass
```

---

## ➕ Добавление новых функций

### 🎯 Пошаговый процесс

#### 1️⃣ Анализ требований

```markdown
## Новая функция: Система лояльности

### Требования:
- Накопление баллов за заказы
- Обмен баллов на скидки
- Уровни лояльности (Бронза, Серебро, Золото)

### Пользовательские истории:
- Как клиент, я хочу накапливать баллы за заказы
- Как клиент, я хочу обменивать баллы на скидки
- Как админ, я хочу управлять системой лояльности
```

#### 2️⃣ Проектирование доменной модели

```python
# domain/entities/loyalty.py
@dataclass
class LoyaltyProgram:
    """Программа лояльности."""
    id: str
    name: str
    points_per_ruble: int  # Баллов за рубль
    levels: List[LoyaltyLevel]
    is_active: bool

@dataclass
class LoyaltyLevel:
    """Уровень лояльности."""
    name: str
    min_points: int
    discount_percent: int

@dataclass
class UserLoyalty:
    """Лояльность пользователя."""
    user_id: str
    total_points: int
    current_level: LoyaltyLevel
    points_used: int
    points_earned: int
```

#### 3️⃣ Создание репозитория

```python
# domain/repositories/loyalty_repository.py
class LoyaltyRepository(ABC):
    """Интерфейс репозитория лояльности."""
    
    @abstractmethod
    async def get_user_loyalty(self, user_id: str) -> Optional[UserLoyalty]:
        """Получение лояльности пользователя."""
        pass
    
    @abstractmethod
    async def update_user_loyalty(self, user_loyalty: UserLoyalty) -> UserLoyalty:
        """Обновление лояльности пользователя."""
        pass
    
    @abstractmethod
    async def get_loyalty_program(self) -> Optional[LoyaltyProgram]:
        """Получение программы лояльности."""
        pass
```

#### 4️⃣ Реализация репозитория

```python
# infrastructure/database/repositories/loyalty_repository_impl.py
class LoyaltyRepositoryImpl(LoyaltyRepository):
    """Реализация репозитория лояльности."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_loyalty(self, user_id: str) -> Optional[UserLoyalty]:
        """Получение лояльности пользователя."""
        result = await self.session.execute(
            select(UserLoyaltyModel).where(UserLoyaltyModel.user_id == user_id)
        )
        db_loyalty = result.scalar_one_or_none()
        
        if not db_loyalty:
            return None
        
        return self._model_to_entity(db_loyalty)
    
    def _model_to_entity(self, db_loyalty: UserLoyaltyModel) -> UserLoyalty:
        """Преобразование модели в сущность."""
        return UserLoyalty(
            user_id=db_loyalty.user_id,
            total_points=db_loyalty.total_points,
            current_level=self._get_level_by_points(db_loyalty.total_points),
            points_used=db_loyalty.points_used,
            points_earned=db_loyalty.points_earned
        )
```

#### 5️⃣ Создание сервиса

```python
# domain/services/loyalty_service.py
class LoyaltyService:
    """Сервис лояльности."""
    
    def __init__(self, loyalty_repository: LoyaltyRepository):
        self.loyalty_repository = loyalty_repository
    
    async def add_points(self, user_id: str, order_amount: int) -> UserLoyalty:
        """Добавление баллов за заказ."""
        loyalty = await self.loyalty_repository.get_user_loyalty(user_id)
        if not loyalty:
            loyalty = UserLoyalty(
                user_id=user_id,
                total_points=0,
                current_level=self._get_bronze_level(),
                points_used=0,
                points_earned=0
            )
        
        # Получение программы лояльности
        program = await self.loyalty_repository.get_loyalty_program()
        points_to_add = int(order_amount / 100 * program.points_per_ruble)
        
        # Обновление баллов
        loyalty.total_points += points_to_add
        loyalty.points_earned += points_to_add
        loyalty.current_level = self._get_level_by_points(loyalty.total_points)
        
        return await self.loyalty_repository.update_user_loyalty(loyalty)
    
    async def use_points(self, user_id: str, points_to_use: int) -> int:
        """Использование баллов для скидки."""
        loyalty = await self.loyalty_repository.get_user_loyalty(user_id)
        if not loyalty or loyalty.total_points < points_to_use:
            raise InsufficientPointsError("Недостаточно баллов")
        
        loyalty.total_points -= points_to_use
        loyalty.points_used += points_to_use
        
        await self.loyalty_repository.update_user_loyalty(loyalty)
        
        # Возвращаем размер скидки в копейках
        return int(points_to_use * 100)  # 1 балл = 1 рубль
```

#### 6️⃣ Создание обработчиков

```python
# infrastructure/telegram/handlers/loyalty_handler.py
class LoyaltyHandler(BaseHandler):
    """Обработчик лояльности."""
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков."""
        self.router.message.register(
            self.handle_loyalty_command,
            F.text == "/loyalty"
        )
        self.router.callback_query.register(
            self.handle_loyalty_callback,
            F.data.startswith("loyalty:")
        )
    
    async def handle_loyalty_command(self, message: Message) -> None:
        """Обработка команды /loyalty."""
        user_id = message.from_user.id
        
        loyalty_service = await get_loyalty_service()
        loyalty = await loyalty_service.get_user_loyalty(user_id)
        
        if not loyalty:
            text = "🎁 <b>Программа лояльности</b>\n\nУ вас пока нет баллов."
        else:
            text = f"""🎁 <b>Ваша лояльность</b>

🏆 <b>Уровень:</b> {loyalty.current_level.name}
⭐ <b>Баллов:</b> {loyalty.total_points}
💰 <b>Заработано:</b> {loyalty.points_earned}
🛒 <b>Потрачено:</b> {loyalty.points_used}

💡 <b>Как получить баллы:</b>
• 1 балл за каждый потраченный рубль
• Бонусы за регулярные заказы
• Специальные акции"""
        
        keyboard = LoyaltyKeyboard.get_loyalty_menu()
        await message.answer(text=text, reply_markup=keyboard)
```

#### 7️⃣ Создание клавиатур

```python
# infrastructure/telegram/keyboards/loyalty_keyboard.py
class LoyaltyKeyboard(BaseKeyboard):
    """Клавиатура лояльности."""
    
    @staticmethod
    def get_loyalty_menu() -> InlineKeyboardMarkup:
        """Главное меню лояльности."""
        buttons = [
            [
                InlineKeyboardButton(
                    text="🎁 Использовать баллы",
                    callback_data="loyalty:use_points"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 История баллов",
                    callback_data="loyalty:history"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Уровни лояльности",
                    callback_data="loyalty:levels"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
        return BaseKeyboard.create_inline_keyboard(buttons)
```

#### 8️⃣ Интеграция с существующими сервисами

```python
# domain/services/order_service.py
class OrderService:
    """Сервис заказов с интеграцией лояльности."""
    
    async def create_order(self, user_id: str, cart: Cart, use_loyalty_points: bool = False) -> Order:
        """Создание заказа с учетом лояльности."""
        # Создание заказа
        order = Order(...)
        
        # Применение баллов лояльности
        if use_loyalty_points:
            loyalty_service = await get_loyalty_service()
            loyalty = await loyalty_service.get_user_loyalty(user_id)
            
            if loyalty and loyalty.total_points > 0:
                # Использовать все доступные баллы
                discount = await loyalty_service.use_points(user_id, loyalty.total_points)
                order.discount = discount
                order.total -= discount
        
        # Сохранение заказа
        saved_order = await self.order_repository.create(order)
        
        # Начисление баллов за заказ
        loyalty_service = await get_loyalty_service()
        await loyalty_service.add_points(user_id, saved_order.total)
        
        return saved_order
```

#### 9️⃣ Создание тестов

```python
# tests/unit/test_loyalty_service.py
class TestLoyaltyService:
    """Тесты сервиса лояльности."""
    
    @pytest.fixture
    def loyalty_service(self):
        """Фикстура сервиса лояльности."""
        mock_repository = Mock(spec=LoyaltyRepository)
        return LoyaltyService(mock_repository)
    
    async def test_add_points_new_user(self, loyalty_service):
        """Тест добавления баллов новому пользователю."""
        # Arrange
        user_id = "test_user"
        order_amount = 1000  # 1000 рублей
        
        loyalty_service.loyalty_repository.get_user_loyalty.return_value = None
        loyalty_service.loyalty_repository.get_loyalty_program.return_value = LoyaltyProgram(
            id="1",
            name="Test Program",
            points_per_ruble=1,
            levels=[],
            is_active=True
        )
        
        # Act
        result = await loyalty_service.add_points(user_id, order_amount)
        
        # Assert
        assert result.total_points == 1000
        assert result.points_earned == 1000
        loyalty_service.loyalty_repository.update_user_loyalty.assert_called_once()
```

#### 🔟 Обновление документации

```markdown
# Система лояльности

## Описание
Система накопления и использования баллов лояльности для клиентов кафе.

## Функции
- Накопление баллов за заказы
- Обмен баллов на скидки
- Уровни лояльности
- История операций

## API
- `LoyaltyService.add_points()` - добавление баллов
- `LoyaltyService.use_points()` - использование баллов
- `LoyaltyService.get_user_loyalty()` - получение информации о лояльности
```

---

## 🧪 Тестирование

### 🎯 Типы тестов

#### 🔬 Юнит-тесты

```python
# tests/unit/test_order_service.py
class TestOrderService:
    """Тесты сервиса заказов."""
    
    @pytest.fixture
    def order_service(self):
        """Фикстура сервиса заказов."""
        mock_repository = Mock(spec=OrderRepository)
        return OrderService(mock_repository)
    
    async def test_create_order_success(self, order_service):
        """Тест успешного создания заказа."""
        # Arrange
        user_id = "test_user"
        cart = Cart(user_id=user_id, items=[], total_price=1000)
        
        expected_order = Order(
            order_id="test_order",
            user_id=user_id,
            items=[],
            total=1000,
            status=OrderStatus.PENDING
        )
        
        order_service.order_repository.create.return_value = expected_order
        
        # Act
        result = await order_service.create_order(user_id, cart)
        
        # Assert
        assert result == expected_order
        order_service.order_repository.create.assert_called_once()
    
    async def test_create_order_empty_cart(self, order_service):
        """Тест создания заказа с пустой корзиной."""
        # Arrange
        user_id = "test_user"
        cart = Cart(user_id=user_id, items=[], total_price=0)
        
        # Act & Assert
        with pytest.raises(EmptyCartError):
            await order_service.create_order(user_id, cart)
```

#### 🔗 Интеграционные тесты

```python
# tests/integration/test_order_flow.py
class TestOrderFlow:
    """Интеграционные тесты процесса заказа."""
    
    @pytest.fixture
    async def test_session(self):
        """Фикстура тестовой сессии БД."""
        async with get_test_session() as session:
            yield session
    
    async def test_complete_order_flow(self, test_session):
        """Тест полного процесса заказа."""
        # Arrange
        user_id = "test_user"
        
        # Создание пользователя
        user_service = UserService(UserRepositoryImpl(test_session))
        user = await user_service.create_user(user_id, "Test User")
        
        # Создание меню
        menu_service = MenuService(MenuRepositoryImpl(test_session))
        category = await menu_service.create_category("Test Category")
        menu_item = await menu_service.create_menu_item(
            category_id=category.id,
            name="Test Item",
            price=500
        )
        
        # Добавление в корзину
        cart_service = CartService(CartRepositoryImpl(test_session))
        await cart_service.add_item(user_id, menu_item.id, 2)
        
        # Act - создание заказа
        order_service = OrderService(OrderRepositoryImpl(test_session))
        order = await order_service.create_order(user_id, await cart_service.get_cart(user_id))
        
        # Assert
        assert order.user_id == user_id
        assert order.total == 1000
        assert order.status == OrderStatus.PENDING
        assert len(order.items) == 1
        assert order.items[0].quantity == 2
```

#### 🎭 Тесты с моками

```python
# tests/unit/test_notification_service.py
class TestNotificationService:
    """Тесты сервиса уведомлений."""
    
    @pytest.fixture
    def mock_bot(self):
        """Фикстура мока бота."""
        return Mock(spec=Bot)
    
    @pytest.fixture
    def notification_service(self, mock_bot):
        """Фикстура сервиса уведомлений."""
        return NotificationService(mock_bot, Mock())
    
    async def test_send_order_notification(self, notification_service, mock_bot):
        """Тест отправки уведомления о заказе."""
        # Arrange
        order = Order(
            order_id="test_order",
            user_id="test_user",
            items=[],
            total=1000,
            status=OrderStatus.PENDING
        )
        
        # Act
        await notification_service.send_order_notification(order)
        
        # Assert
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert "test_order" in call_args[1]["text"]
```

### 🏃‍♂️ Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=. --cov-report=html

# Запуск конкретного теста
pytest tests/unit/test_order_service.py::TestOrderService::test_create_order_success

# Запуск с подробным выводом
pytest -v

# Запуск только быстрых тестов
pytest -m "not slow"
```

### 📊 Покрытие кода

```bash
# Генерация отчета о покрытии
pytest --cov=. --cov-report=html --cov-report=term

# Просмотр отчета
open htmlcov/index.html
```

---

## 🎨 Стиль кода

### 📝 Форматирование

#### 🖤 Black

```bash
# Установка
pip install black

# Форматирование
black .

# Проверка
black --check .
```

#### 📦 isort

```bash
# Установка
pip install isort

# Сортировка импортов
isort .

# Проверка
isort --check-only .
```

### 🔍 Линтинг

#### 🐍 flake8

```bash
# Установка
pip install flake8

# Проверка
flake8 .

# Конфигурация в setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv
```

#### 🔍 mypy

```bash
# Установка
pip install mypy

# Проверка типов
mypy .

# Конфигурация в mypy.ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### 📋 Pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

```bash
# Установка pre-commit
pip install pre-commit
pre-commit install
```

---

## 🔄 CI/CD

### 🐙 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Check types with mypy
      run: mypy .
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 🐳 Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 cafe-bot && chown -R cafe-bot:cafe-bot /app
USER cafe-bot

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "-m", "app.main"]
```

### 🚀 Развертывание

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/cafe-bot
          git pull origin main
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml build
          docker-compose -f docker-compose.prod.yml up -d
```

---

## 🐛 Отладка

### 🔍 Логирование

```python
# infrastructure/logging/logger.py
import logging
import sys
from typing import Any, Dict

class CafeBotLogger:
    """Логгер для приложения."""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Консольный хендлер
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Файловый хендлер
        file_handler = logging.FileHandler('logs/cafe_bot.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Информационное сообщение."""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Сообщение об ошибке."""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Отладочное сообщение."""
        self.logger.debug(message, extra=kwargs)
```

### 🔧 Отладочные инструменты

#### 🐛 pdb

```python
# Отладка с pdb
import pdb

async def create_order(self, user_id: str, cart: Cart) -> Order:
    """Создание заказа с отладкой."""
    pdb.set_trace()  # Точка останова
    
    # Код для отладки
    order = Order(...)
    return order
```

#### 🔍 aiomonitor

```python
# Отладка асинхронного кода
import aiomonitor

async def main():
    with aiomonitor.start_monitor():
        # Запуск приложения
        await run_app()

if __name__ == "__main__":
    asyncio.run(main())
```

### 📊 Профилирование

#### ⏱️ cProfile

```python
# Профилирование производительности
import cProfile
import pstats

def profile_function():
    """Профилирование функции."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Код для профилирования
    result = some_function()
    
    profiler.disable()
    
    # Анализ результатов
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

#### 📈 memory_profiler

```python
# Профилирование памяти
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Функция с профилированием памяти."""
    data = []
    for i in range(1000000):
        data.append(i)
    return data
```

---

## ⚡ Производительность

### 🚀 Оптимизация

#### 🗄️ Кэширование

```python
# Кэширование с Redis
import redis
import json
from typing import Any, Optional

class CacheService:
    """Сервис кэширования."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Получение из кэша."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Сохранение в кэш."""
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str) -> None:
        """Удаление из кэша."""
        await self.redis.delete(key)
```

#### 🔄 Connection Pooling

```python
# Пул соединений с БД
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

#### 📊 Batch операции

```python
# Пакетная обработка
async def batch_create_orders(self, orders: List[Order]) -> List[Order]:
    """Пакетное создание заказов."""
    db_orders = [self._entity_to_model(order) for order in orders]
    
    self.session.add_all(db_orders)
    await self.session.commit()
    
    return [self._model_to_entity(db_order) for db_order in db_orders]
```

### 📈 Мониторинг производительности

#### 📊 Prometheus метрики

```python
# Метрики производительности
from prometheus_client import Counter, Histogram, Gauge

# Счетчики
orders_total = Counter('orders_total', 'Total orders', ['status'])
errors_total = Counter('errors_total', 'Total errors', ['type'])

# Гистограммы
order_duration = Histogram('order_duration_seconds', 'Order processing time')
db_query_duration = Histogram('db_query_duration_seconds', 'Database query time')

# Gauges
active_users = Gauge('active_users', 'Number of active users')
queue_size = Gauge('queue_size', 'Queue size')
```

#### 📈 Grafana дашборды

```json
{
  "dashboard": {
    "title": "Cafe Bot Performance",
    "panels": [
      {
        "title": "Orders per minute",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(orders_total[1m])",
            "legendFormat": "Orders/min"
          }
        ]
      },
      {
        "title": "Response time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, order_duration_seconds_bucket)",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

---

## 🔒 Безопасность

### 🛡️ Принципы безопасности

#### 🔐 Аутентификация и авторизация

```python
# Middleware для проверки прав
class AuthMiddleware:
    """Middleware для аутентификации."""
    
    async def __call__(self, handler, event, data):
        """Проверка прав доступа."""
        user_id = data.get("user_id")
        
        if not user_id:
            raise UnauthorizedError("User not authenticated")
        
        # Проверка роли пользователя
        user_service = await get_user_service()
        user = await user_service.get_user_by_telegram_id(user_id)
        
        if not user:
            raise UnauthorizedError("User not found")
        
        # Добавление пользователя в контекст
        data["user"] = user
        
        return await handler(event, data)
```

#### 🔒 Валидация входных данных

```python
# Валидация с Pydantic
from pydantic import BaseModel, validator

class OrderCreateRequest(BaseModel):
    """Запрос на создание заказа."""
    user_id: str
    items: List[OrderItemRequest]
    delivery_address: Optional[str] = None
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Валидация ID пользователя."""
        if not v or len(v) < 1:
            raise ValueError('Invalid user ID')
        return v
    
    @validator('items')
    def validate_items(cls, v):
        """Валидация списка товаров."""
        if not v or len(v) == 0:
            raise ValueError('Order must contain at least one item')
        return v
```

#### 🛡️ Защита от атак

```python
# Rate limiting
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time

class RateLimiter:
    """Ограничение частоты запросов."""
    
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def is_allowed(self, user_id: str) -> bool:
        """Проверка лимита запросов."""
        now = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Очистка старых запросов
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window
        ]
        
        # Проверка лимита
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # Добавление текущего запроса
        self.requests[user_id].append(now)
        return True
```

### 🔐 Шифрование

#### 🔑 Хеширование паролей

```python
# Хеширование с bcrypt
import bcrypt

class PasswordService:
    """Сервис для работы с паролями."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Проверка пароля."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

#### 🔐 Шифрование чувствительных данных

```python
# Шифрование с cryptography
from cryptography.fernet import Fernet

class EncryptionService:
    """Сервис шифрования."""
    
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Шифрование данных."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Расшифровка данных."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

---

## 📞 Поддержка

### 🆘 Техническая поддержка

- **📧 Email**: dev-support@example.com
- **📱 Telegram**: @dev_support_bot
- **🌐 Сайт**: https://dev.example.com

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
