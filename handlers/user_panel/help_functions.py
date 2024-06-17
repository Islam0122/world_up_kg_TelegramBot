from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from filter.chat_types import ChatTypeFilter
from handlers.user_panel.start_functions import user_preferences

help_private_router = Router()
help_private_router.message.filter(ChatTypeFilter(['private']))

# Help texts for clients and administrators in English and Russian
help_texts = {
    'ru': {
        'client': (
            "Список доступных команд:\n"
            "/start - 🚀 Начать общение\n"
            "/catalog - 🛍️ Посмотреть каталог товаров\n"
            "/popular_products - 🚀 Популярные товары\n"
            "/search - 🔍 Поиск товаров\n"
            "/review - ✍️ Оставить отзыв\n"
            "/about_us - ℹ️ О магазине\n"
            "/help - 🆘 Получить помощь\n\n"
            "Если у вас есть вопросы, напишите сюда ({admin_account}), чтобы связаться с администратором."
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
        )
    },
    'en': {
        'client': (
            "List of available commands:\n"
            "/start - 🚀 Start chatting\n"
            "/catalog - 🛍️ View product catalog\n"
            "/popular_products - 🚀 Popular products\n"
            "/search - 🔍 Search products\n"
            "/review - ✍️ Leave a review\n"
            "/about_us - ℹ️ About us\n"
            "/help - 🆘 Get help\n\n"
            "If you have any questions, please contact us here ({admin_account})."
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
        )
    }
}

# Inline keyboard to return to main menu
def inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🏠 Return to main menu", callback_data="help"),
    )
    return keyboard.adjust().as_markup()

# Message handler for /help command
@help_private_router.message((Command("help")) | (types.ContentTypes.TEXT & (types.text.lower().contains('🆘 Помощь') | types.text.lower() == 'help')))
async def help_command_message(message: types.Message, bot: Bot) -> None:
    user_id = message.from_user.id
    language = user_preferences.get(user_id, 'ru')  # Assuming 'ru' is the default language
    admin_account = 'YOUR_ADMIN_ACCOUNT'  # Replace with your actual admin contact

    if user_id in bot.my_admins_list:
        await message.answer_photo(
            photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
            caption=help_texts[language]['admin'].format(admin_account=admin_account),
            reply_markup=inline_keyboard(),
        )
    else:
        await message.answer_photo(
            photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
            caption=help_texts[language]['client'].format(admin_account=admin_account),
            reply_markup=inline_keyboard(),
        )

# Callback handler for returning to main menu
@help_private_router.callback_query((Command("help")) & (types.ContentTypes.TEXT & (types.text.lower().contains('🏠 Return to main menu') | types.text.lower() == 'help')))
async def help_command_callback_query(query: types.CallbackQuery, bot: Bot) -> None:
    message = query.message
    user_id = query.from_user.id
    language = user_preferences.get(user_id, 'ru')  # Assuming 'ru' is the default language

    await message.edit_caption(
        caption=help_texts[language]['client'],
        reply_markup=inline_keyboard(),
    )