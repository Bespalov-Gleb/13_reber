"""Script to add test data to the database."""

import asyncio
from dotenv import load_dotenv

from app.config import get_settings
from infrastructure.database.connection import init_database, _session_maker
from infrastructure.database.models import CategoryModel, MenuItemModel
from shared.utils.helpers import generate_id

load_dotenv()


async def add_test_data():
    """Add test categories and menu items."""
    settings = get_settings()
    
    # Initialize database
    await init_database(settings.database_url)
    
    async with _session_maker() as session:
        # Add categories
        categories_data = [
            {
                "name": "🍕 Пицца",
                "description": "Свежая пицца на тонком тесте",
                "image_url": None,
                "is_active": True
            },
            {
                "name": "🍔 Бургеры",
                "description": "Сочные бургеры с мясом",
                "image_url": None,
                "is_active": True
            },
            {
                "name": "🍝 Паста",
                "description": "Итальянская паста с разными соусами",
                "image_url": None,
                "is_active": True
            },
            {
                "name": "🥤 Напитки",
                "description": "Прохладительные напитки",
                "image_url": None,
                "is_active": True
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = CategoryModel(
                id=generate_id(),
                name=cat_data["name"],
                description=cat_data["description"],
                image_url=cat_data["image_url"],
                is_active=cat_data["is_active"]
            )
            session.add(category)
            categories.append(category)
        
        await session.commit()
        print("✅ Categories added successfully")
        
        # Add menu items
        menu_items_data = [
            # Пицца
            {
                "name": "Маргарита",
                "description": "Классическая пицца с томатами и моцареллой",
                "price": 450,
                "category_id": categories[0].id,
                "ingredients": "Тесто, томатный соус, моцарелла, базилик",
                "allergens": "Глютен, молочные продукты",
                "weight": "350г",
                "calories": 280,
                "image_url": None,
                "is_available": True
            },
            {
                "name": "Пепперони",
                "description": "Острая пицца с колбасой пепперони",
                "price": 550,
                "category_id": categories[0].id,
                "ingredients": "Тесто, томатный соус, моцарелла, пепперони",
                "allergens": "Глютен, молочные продукты",
                "weight": "380г",
                "calories": 320,
                "image_url": None,
                "is_available": True
            },
            # Бургеры
            {
                "name": "Чизбургер",
                "description": "Классический бургер с сыром",
                "price": 350,
                "category_id": categories[1].id,
                "ingredients": "Булочка, котлета, сыр, салат, томат, лук",
                "allergens": "Глютен, молочные продукты",
                "weight": "250г",
                "calories": 450,
                "image_url": None,
                "is_available": True
            },
            {
                "name": "Биг Мак",
                "description": "Большой бургер с двойной котлетой",
                "price": 450,
                "category_id": categories[1].id,
                "ingredients": "Булочка, 2 котлеты, сыр, салат, томат, лук, соус",
                "allergens": "Глютен, молочные продукты",
                "weight": "350г",
                "calories": 650,
                "image_url": None,
                "is_available": True
            },
            # Паста
            {
                "name": "Карбонара",
                "description": "Паста с беконом и сливочным соусом",
                "price": 400,
                "category_id": categories[2].id,
                "ingredients": "Спагетти, бекон, яйца, пармезан, сливки",
                "allergens": "Глютен, молочные продукты, яйца",
                "weight": "300г",
                "calories": 380,
                "image_url": None,
                "is_available": True
            },
            {
                "name": "Болоньезе",
                "description": "Паста с мясным соусом",
                "price": 420,
                "category_id": categories[2].id,
                "ingredients": "Спагетти, фарш, томаты, лук, морковь",
                "allergens": "Глютен",
                "weight": "320г",
                "calories": 400,
                "image_url": None,
                "is_available": True
            },
            # Напитки
            {
                "name": "Кока-Кола",
                "description": "Классическая газировка",
                "price": 120,
                "category_id": categories[3].id,
                "ingredients": "Вода, сахар, кофеин, ароматизаторы",
                "allergens": "Нет",
                "weight": "330мл",
                "calories": 140,
                "image_url": None,
                "is_available": True
            },
            {
                "name": "Сок апельсиновый",
                "description": "Свежевыжатый апельсиновый сок",
                "price": 150,
                "category_id": categories[3].id,
                "ingredients": "Апельсины",
                "allergens": "Нет",
                "weight": "250мл",
                "calories": 110,
                "image_url": None,
                "is_available": True
            }
        ]
        
        for item_data in menu_items_data:
            menu_item = MenuItemModel(
                id=generate_id(),
                name=item_data["name"],
                description=item_data["description"],
                price=item_data["price"],
                category_id=item_data["category_id"],
                ingredients=item_data["ingredients"],
                allergens=item_data["allergens"],
                weight=item_data["weight"],
                calories=item_data["calories"],
                image_url=item_data["image_url"],
                is_available=item_data["is_available"]
            )
            session.add(menu_item)
        
        await session.commit()
        print("✅ Menu items added successfully")
        print(f"✅ Added {len(categories)} categories and {len(menu_items_data)} menu items")


if __name__ == "__main__":
    asyncio.run(add_test_data())