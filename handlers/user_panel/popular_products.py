import asyncio
import random
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from googletrans import Translator
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_get_products, orm_get_product
from filter.chat_types import ChatTypeFilter
from handlers.user_panel.start_functions import user_preferences

popular_products_router = Router()
popular_products_router.message.filter(ChatTypeFilter(["private"]))
messages_to_delete = []


update_messages = {
    'ru': "Обновление списка...",
    'en': "Updating the list..."
}

translator = Translator()

# Translation dictionaries
product_texts = {
    'ru': {
        'id': '🆔 ID:',
        'name': '🏷 Название:',
        'description': '📝 Описание:',
        'section': '🔍 Раздел:',
        'category': '📦 Категория:',
        'gender': '👤Тип :',
        'size': '📏 Размер:',
        'price': '💰 Цена:',
        'buy': 'Купить',
        'update': 'Обновить'
    },
    'en': {
        'id': '🆔 ID:',
        'name': '🏷 Name:',
        'description': '📝 Description:',
        'section': '🔍 Section:',
        'category': '📦 Category:',
        'gender': '👤Type:',
        'size': '📏 Size:',
        'price': '💰 Price:',
        'buy': 'Buy',
        'update': 'Update'
    }
}
@popular_products_router.message(F.text.lower() == "🚀 популярные товары")
@popular_products_router.message(Command("popular_products"))
async def popular_products(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id

    # Установка языка по умолчанию на русский, если не указано
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    # Pass the language to send_random_products
    await send_random_products(message, session, language)


@popular_products_router.callback_query(F.data.startswith("popular_products"))
async def popular_products_callback_handler(query: types.CallbackQuery, session: AsyncSession):
    user_id = query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    # Pass the language to send_random_products
    await send_random_products(query.message, session, language)


# Handler for updating popular products
@popular_products_router.callback_query(F.data.startswith("update"))
async def popular_products_update(query: types.CallbackQuery, session: AsyncSession):
    try:
        user_id = query.from_user.id
        language = user_preferences.get(user_id, {}).get('language', 'ru')
        update_msg = update_messages[language]

        await query.answer(update_msg)

        # Send a new message indicating the update
        update_message = await query.message.answer(update_msg)

        # Sequence of messages indicating progress
        for progress in ["1", "2", "3", "......"]:
            progress_message = await query.message.answer(progress)
            await asyncio.sleep(2)
            await progress_message.delete()

        # Send new random products
        await send_random_products(update_message, session, language)

        # Provide feedback that the list has been updated
        await query.answer(update_msg)

    except Exception as e:
        print(f"An error occurred: {e}")


async def send_random_products(message: types.Message, session: AsyncSession, language='ru'):
    products = await orm_get_products(session)
    random_products = random.choices(products, k=min(len(products), 3))
    texts = product_texts[language]

    for product in random_products:
        if language == 'en':
            product_name = translator.translate(product.name, src='ru', dest='en').text
            product_description = translator.translate(product.description, src='ru', dest='en').text
            section = translator.translate(product.section, src='ru', dest='en').text
            category = translator.translate(product.category, src='ru', dest='en').text
            gender = translator.translate(product.gender, src='ru', dest='en').text
            price = translator.translate(str(product.price), src='ru', dest='en').text
        else:
            product_name = product.name
            product_description = product.description
            section = product.section
            category = product.category
            gender = product.gender
            price = str(product.price)

        size_info = f"<b>{texts['size']}</b> {product.size}\n" if product.section.lower() != 'другие' else ""

        description_text = (
            f"<b>{texts['id']}</b> {product.id}\n"
            f"<b>{texts['name']}</b> {product_name}\n"
            f"<b>{texts['description']}</b> {product_description}\n"
            f"<b>{texts['section']}</b> {section}\n"
            f"<b>{texts['category']}</b> {category}\n"
            f"<b>{texts['gender']}</b> {gender}\n"
            f"{size_info}"
            f"<b>{texts['price']}</b> {price}\n"
        )

        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"{texts['buy']} {product_name}", callback_data=f"buy_{product.id}"),
                    InlineKeyboardButton(text=texts['update'], callback_data="update"),
                ]
            ]
        )

        await message.answer_photo(
            product.image,
            caption=description_text,
            reply_markup=inline_kb
        )