from aiogram import F, types, Router ,Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.config import admin_account
from filter.chat_types import ChatTypeFilter
from aiogram import types, Dispatcher

from handlers.user_panel.start_functions import user_preferences

unknown_private_router = Router()
unknown_private_router.message.filter(ChatTypeFilter(['private']))


# Обработчик для неизвестных команд
messages = {
    'ru': {
        'unknown_command': (
            f"Извините, я не понял ваш запрос 😕. Если вам нужна помощь, попробуйте "
            f"воспользоваться командой /help или свяжитесь с администратором -> {admin_account}."
        )
    },
    'en': {
        'unknown_command': (
            f"Sorry, I didn't understand your request 😕. If you need help, try using "
            f"the /help command or contact the administrator -> {admin_account}."
        )
    }
}


@unknown_private_router.message()
async def unknown_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}  # Default language is Russian

    language = user_preferences[user_id]['language']
    response_message = messages[language]['unknown_command']

    await message.reply(response_message, parse_mode="Markdown")