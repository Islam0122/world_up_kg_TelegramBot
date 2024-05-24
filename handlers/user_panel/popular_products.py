import random

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filter.chat_types import ChatTypeFilter, IsAdmin
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product

from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

popular_products_router = Router()
popular_products_router.message.filter(ChatTypeFilter(["private"]))


@popular_products_router.message(F.text.lower() == "🚀 Актуальные товары")
@popular_products_router.message(Command("popular_products"))
async def popular_products_at_product(message: types.Message, session: AsyncSession):
    products = await orm_get_products(session)
    random_products = random.choices(products, k=min(len(products), 5))
    for product in random_products:
        if product.section.lower() == 'другие':  # Check for lowercase 'другие'
            size_info = ""  # Если раздел "Другие", размер не выводится
        else:
            size_info=f"<b>📏 Размер:</b> {product.size}\n"
        description_text = (
            f"<b>🆔 ID:</b> {product.id}\n"
            f"<b>🏷 Название:</b> {product.name}\n"
            f"<b>📝 Описание:</b> {product.description}\n"
            f"<b>🔍 Раздел:</b> {product.section}\n"
            f"<b>📦 Категория:</b> {product.category}\n"
            f"<b>👤 Тип:</b> {product.gender}\n"
            f"{size_info}"  # Вставляем информацию о размере
            f"<b>💰 Цена:</b> {product.price}\n"
        )

        await message.answer_photo(
            product.image,
            caption=description_text,
            reply_markup=get_callback_btns(
                btns={
                    f"Купить {product.name}": f"buy_{product.id}",
                }
            ),
        )


@popular_products_router.callback_query((F.data.startswith("popular_products")))
async def popular_products_callback_handler(query: types.CallbackQuery, session: AsyncSession):
    message = query.message
    products = await orm_get_products(session)
    random_products = random.choices(products, k=min(len(products), 5))
    for product in random_products:
        if product.section.lower() == 'другие':  # Check for lowercase 'другие'
            size_info = ""  # Если раздел "Другие", размер не выводится
        else:
            size_info=f"<b>📏 Размер:</b> {product.size}\n"

        description_text = (
            f"<b>🆔 ID:</b> {product.id}\n"
            f"<b>🏷 Название:</b> {product.name}\n"
            f"<b>📝 Описание:</b> {product.description}\n"
            f"<b>🔍 Раздел:</b> {product.section}\n"
            f"<b>📦 Категория:</b> {product.category}\n"
            f"<b>👤 Пол :</b> {product.gender}\n"
            f"{size_info}"  # Вставляем информацию о размере
            f"<b>💰 Цена:</b> {product.price}\n"
          )

        await message.answer_photo(
            product.image,
            caption=description_text,
            reply_markup=get_callback_btns(
                btns={
                    f"Купить {product.name}": f"buy_{product.id}",
                }
            ),
        )