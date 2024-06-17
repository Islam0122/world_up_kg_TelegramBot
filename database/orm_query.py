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
        name=data["name"],
        description=data["description"],
        price=data["price"],
        image=data["image"],
        section=data["section"],
        category=data["category"],
        gender=data["gender"],
        size=data["size"],
    )
    session.add(obj)
    await session.commit()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        image=data["image"],
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


async def orm_search_products(session: AsyncSession, search_query: str):
    try:
        search_id = int(search_query)
    except ValueError:
        search_id = None

    query = select(Product).filter(
        or_(
            Product.name.ilike(f'%{search_query}%'),
            Product.id == search_id,
            Product.price.ilike(f'%{search_query}%')
        )
    )
    result = await session.execute(query)
    return result.scalars().all()
