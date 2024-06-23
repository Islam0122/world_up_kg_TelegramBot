from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .model import Product
from sqlalchemy import or_


async def orm_get_products(session: AsyncSession):
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).filter(Product.id == int(product_id))
    result = await session.execute(query)
    return result.scalar()

# -> ########### Админка: добавить/изменить/удалить товар ####################### <-#

async def orm_add_product(session: AsyncSession, data: dict):
    obj = Product(
        image1=data["image1"],
        image2=data["image2"],
        image3=data["image3"],
        image4=data["image4"],

        name=data["name"],
        description=data["description"],
        price=data["price"],
        section=data["section"],
        category=data["category"],
        gender=data["gender"],
        size=data["size"],
    )
    session.add(obj)
    await session.commit()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(
        image1=data["image1"],
        image2=data["image2"],
        image3=data["image3"],
        image4=data["image4"],

        name=data["name"],
        description=data["description"],
        price=data["price"],
        section=data["section"],
        category=data["category"],
        gender=data["gender"],
        size=data["size"], )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


from googletrans import Translator as GoogleTranslator


# Создание экземпляра переводчика
translator = GoogleTranslator()

# Функция для перевода текста
def translate_text(text, src_lang='auto', dest_lang='ru'):
    translation = translator.translate(text, src=src_lang, dest=dest_lang)
    return translation.text

# Функция для поиска товаров в базе данных
async def orm_search_products(session: AsyncSession, search_query: str):
    try:
        search_id = int(search_query)
    except ValueError:
        search_id = None

    # Переводим запрос перед выполнением поиска
    translated_query = translate_text(search_query)

    # Запрос к базе данных для поиска товаров с использованием ILIKE для частичного совпадения
    query = select(Product).filter(
        or_(
            Product.name.ilike(f'%{translated_query}%'),  # Частичное совпадение по названию продукта
            Product.id == search_id,  # Точное совпадение по ID продукта
            Product.price.ilike(f'%{translated_query}%'),  # Частичное совпадение по цене
            Product.section.ilike(f'%{translated_query}%'),  # Частичное совпадение по разделу
            Product.category.ilike(f'%{translated_query}%'),  # Частичное совпадение по категории
            Product.gender.ilike(f'%{translated_query}%')  # Частичное совпадение по полу
        )
    )

    # Выполняем запрос и возвращаем результат
    result = await session.execute(query)
    return result.scalars().all()
