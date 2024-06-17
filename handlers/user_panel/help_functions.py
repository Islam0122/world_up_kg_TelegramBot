from aiogram import types, Router, Bot, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.config import admin_account
from filter.chat_types import ChatTypeFilter
from handlers.user_panel.start_functions import user_preferences

help_private_router = Router()
help_private_router.message.filter(ChatTypeFilter(['private']))

# Help texts for clients and administrators in English and Russian
help_texts = {
    'ru': {
        'client': (
            f"Список доступных команд:\n"
            f"/start - 🚀 Начать общение\n"
            f"/catalog - 🛍️ Посмотреть каталог товаров\n"
            f"/popular_products - 🚀 Популярные товары\n"
            f"/search - 🔍 Поиск товаров\n"
           f"/review - ✍️ Оставить отзыв\n"
            f"/about_us - ℹ️ О магазине\n"
            f"/help - 🆘 Получить помощь\n\n"
            f"Если у вас есть вопросы, напишите сюда ({admin_account}), чтобы связаться с администратором."
        ),
        'admin': (
            "Список доступных команд для администраторов:\n"
            "/start - 🚀 Начать общение\n"
            "/catalog - 🛍️ Посмотреть каталог товаров\n"
            "/popular_products - 🚀 Популярные товары\n"
            "/search - 🔍 Поиск товаров\n"
            "/review - ✍️ Оставить отзыв\n"
            "/about_us - ℹ️ О магазине\n"
            "/help - 🆘 Получить помощь\n"
            "/start_admin - 🌟 Панель администратора\n"
            "/add_product - ➕ Добавить товар\n"
            "/admin_search - 🔍 Поиск товаров для админа\n"
        ),
        'return': ("🏠 Вернуться в главное меню")},


    'en': {
        'client': (
            f"List of available commands:\n"
            f"/start - 🚀 Start chatting\n"
           f"/catalog - 🛍️ View product catalog\n"
            f"/popular_products - 🚀 Popular products\n"
            f"/search - 🔍 Search products\n"
            f"/review - ✍️ Leave a review\n"
            f"/about_us - ℹ️ About us\n"
            f"/help - 🆘 Get help\n\n"
            f"If you have any questions, please contact us here ({admin_account})."
        ),
        'admin': (
            "List of available commands for administrators:\n"
            "/start - 🚀 Start chatting\n"
            "/catalog - 🛍️ View product catalog\n"
            "/popular_products - 🚀 Popular products\n"
            "/search - 🔍 Search products\n"
            "/review - ✍️ Leave a review\n"
            "/about_us - ℹ️ About us\n"
            "/help - 🆘 Get help\n"
            "/start_admin - 🌟 Admin panel\n"
            "/add_product - ➕ Add product\n"
            "/admin_search - 🔍 Search products for admin\n"
        ),
        'return': "🏠 Return to main menu"

    }
}

# Inline keyboard to return to main menu
def inline_keyboard(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=help_texts[language]['return'], callback_data="start"),
    )
    return keyboard.adjust().as_markup()

# Message handler for /help command
@help_private_router.message((F.text.lower().contains('🆘 Помощь')) | (F.text.lower() == 'help'))
@help_private_router.message(Command("help"))
async def help_command_message(message: types.Message, bot: Bot) -> None:
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
  # Replace with your actual admin contact

    if user_id in bot.my_admins_list:
        await message.answer_photo(
            photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
            caption=help_texts[language]['admin'],
            reply_markup=inline_keyboard(language),
        )
    else:
        await message.answer_photo(
            photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
            caption=help_texts[language]['client'],
            reply_markup=inline_keyboard(language),
        )

# Callback handler for returning to main menu
@help_private_router.callback_query(F.data.startswith('help'))
async def help_command_callback_query(query: types.CallbackQuery, bot: Bot) -> None:
    message = query.message
    user_id = query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    await message.edit_caption(
        caption=help_texts[language]['client'],
        reply_markup=inline_keyboard(language),
    )