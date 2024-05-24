from aiogram import F, types, Router ,Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.config import admin_account
from filter.chat_types import ChatTypeFilter
from aiogram import types, Dispatcher

unknown_private_router = Router()
unknown_private_router.message.filter(ChatTypeFilter(['private']))


# Обработчик для неизвестных команд
@unknown_private_router.message()
async def unknown_command(message: types.Message):
        await message.reply(
            f"Извините, я не понял ваш запрос 😕. Если вам нужна помощь, попробуйте "
            f"воспользоваться командой /help или свяжитесь с администратором -> {admin_account}. ",
            parse_mode="Markdown"
        )
