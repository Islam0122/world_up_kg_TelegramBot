import random
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_panel.start_functions import user_preferences
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product, \
    orm_search_products, orm_get_products

from keyboard_list.inline import get_callback_btns


# Dictionary of messages in different languages
messages = {
    'ru': {
        'search_instruction': (
            "Введите запрос для поиска товара. Например, чтобы найти товар, "
            "используйте команду /search и укажите название товара, его ID или цену.\n\n"
            "Пример использования:\n"
            "/search Ноутбук 🖥️\n"
            "/search 1234 🆔\n"
            "/search 1000 💰"
        ),
        'no_results': "По запросу '{query}' ничего не найдено.",
    },
    'en': {
        'search_instruction': (
            "Enter a query to search for a product. For example, to find a product, "
            "use the /search command and specify the product name, its ID, or price.\n\n"
            "Example usage:\n"
            "/search Laptop 🖥️\n"
            "/search 1234 🆔\n"
            "/search 1000 💰"
        ),
        'no_results': "No results found for '{query}'.",
    }
}



search_products_router = Router()
search_products_router.message.filter(ChatTypeFilter(["private"]))

# Handler for "/search" command or "🔍 Поиск товаров" message
@search_products_router.message(F.text.lower() == "🔍 Поиск товаров" or F.text.lower() == "/search")
@search_products_router.message(Command("search"))
async def search_command(message: types.Message, session: AsyncSession):
    query = message.text.split(maxsplit=1)[-1].strip()
    user_id = message.from_user.id

    # Set default language to Russian if not specified
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    if query.lower() not in ["/search", "🔍 Поиск товаров"]:
        search_results = await orm_search_products(session, query)

        if search_results:
            for product in search_results:
                size_info = "" if product.section.lower() == 'другие' else f"<b>📏 Размер:</b> {product.size}\n"
                description_text = (
                    f"<b>🆔 ID:</b> {product.id}\n"
                    f"<b>🏷 Название:</b> {product.name}\n"
                    f"<b>📝 Описание:</b> {product.description}\n"
                    f"<b>🔍 Раздел:</b> {product.section}\n"
                    f"<b>📦 Категория:</b> {product.category}\n"
                    f"<b>👤 Пол :</b> {product.gender}\n"
                    f"{size_info}"
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
            no_results_message = messages[language]['no_results'].format(query=query)
            await message.reply(no_results_message)
    else:
        search_instruction_message = messages[language]['search_instruction']
        await message.reply(search_instruction_message)

# Callback handler for search queries
@search_products_router.callback_query((F.data.startswith("search")))
async def search_callback_handler(callback: types.CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id

    # Set default language to Russian if not specified
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    search_instruction_message = messages[language]['search_instruction']
    await callback.message.answer(text=search_instruction_message)