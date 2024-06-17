import asyncio
import random
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_get_products, orm_get_product
from filter.chat_types import ChatTypeFilter

popular_products_router = Router()
popular_products_router.message.filter(ChatTypeFilter(["private"]))
messages_to_delete =[]
@popular_products_router.message(F.text.lower() == "🚀 популярные товары")
@popular_products_router.message(Command("popular_products"))
async def popular_products(message: types.Message, session: AsyncSession):
    await send_random_products(message, session)

@popular_products_router.callback_query((F.data.startswith("popular_products")))
async def popular_products_callback_handler(query: types.CallbackQuery, session: AsyncSession):
    message = query.message
    await send_random_products(message, session)

@popular_products_router.callback_query(F.data.startswith("update"))
async def popular_products_update(query: types.CallbackQuery, session: AsyncSession):
    try:
        await query.answer("Обновление списка...")

        # Send a new message indicating the update
        update_message = await query.message.answer("Обновление списка...")


        original_message = await query.message.answer("1")
        await asyncio.sleep(2)  # Adjust the delay time as needed
        # Delete the original message
        await original_message.delete()
        original_message = await query.message.answer("2")
        await asyncio.sleep(2)  # Adjust the delay time as needed
        # Delete the original message
        await original_message.delete()
        original_message = await query.message.answer("3")
        await asyncio.sleep(2)  # Adjust the delay time as needed
        # Delete the original message
        await original_message.delete()
        original_message = await query.message.answer("......")
        await asyncio.sleep(2)  # Adjust the delay time as needed
        # Delete the original message
        await original_message.delete()

        # Send new random products
        await send_random_products(update_message, session)

        # Provide feedback that the list has been updated
        await query.answer("Список обновлен")

    except Exception as e:
        print(f"An error occurred: {e}")


async def send_random_products(message: types.Message, session: AsyncSession):
    products = await orm_get_products(session)
    random_products = random.choices(products, k=min(len(products), 3))
    for product in random_products:
        if product.section.lower() == 'другие':
            size_info = ""
        else:
            size_info = f"<b>📏 Размер:</b> {product.size}\n"

        description_text = (
            f"<b>🆔 ID:</b> {product.id}\n"
            f"<b>🏷 Название:</b> {product.name}\n"
            f"<b>📝 Описание:</b> {product.description}\n"
            f"<b>🔍 Раздел:</b> {product.section}\n"
            f"<b>📦 Категория:</b> {product.category}\n"
            f"<b>👤 Тип:</b> {product.gender}\n"
            f"{size_info}"
            f"<b>💰 Цена:</b> {product.price}\n"
        )

        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"Купить {product.name}", callback_data=f"buy_{product.id}"),
                    InlineKeyboardButton(text="Обновить", callback_data="update"),
                ]
            ]
        )

        await message.answer_photo(
            product.image,
            caption=description_text,
            reply_markup=inline_kb
        )
