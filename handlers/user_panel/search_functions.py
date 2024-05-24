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
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product, \
    orm_search_products

from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

search_products_router = Router()
search_products_router.message.filter(ChatTypeFilter(["private"]))


@search_products_router.message(F.text.lower() == "🔍 Поиск товаров")
@search_products_router.message(Command("search"))
async def search_command(message: types.Message, session: AsyncSession):
    query = message.text.split(maxsplit=1)[-1]

    if query.lower() not in ["/search", "🔍 Поиск товаров"]:
        # Вызов функции поиска товаров
        search_results = await orm_search_products(session, query)

        if search_results:
            for product in search_results:
                if product.section.lower() == 'другие':  # Check for lowercase 'другие'
                    size_info = ""  # Если раздел "Другие", размер не выводится
                else:
                    size_info = f"<b>📏 Размер:</b> {product.size}\n"
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

        else:
            await message.reply(f"По запросу '{query}' ничего не найдено.")
    else:
        await message.reply(
            "Введите запрос для поиска товара. Например, чтобы найти товар, "
            "используйте команду /search и укажите название товара, его ID или цену.\n\n"
            "Пример использования:\n"
            "/search Ноутбук 🖥️\n"
            "/search 1234 🆔\n"
            "/search 1000 💰"  # Пример запроса по цене
        )


@search_products_router.callback_query((F.data.startswith("search")))
async def search_callback_handler(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.answer(text="Введите запрос для поиска товара. Например, чтобы найти товар, "
                                       "используйте команду /search и укажите название товара, его ID или цену.\n\n"
                                       "Пример использования:\n"
                                       "/search Ноутбук 🖥️\n"
                                       "/search 1234 🆔\n"
                                       "/search 1000 💰")
