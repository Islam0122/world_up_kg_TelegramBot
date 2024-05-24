from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filter.chat_types import ChatTypeFilter, IsAdmin
from keyboard_list.inline import get_callback_btns

admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

# Приветственное сообщение
admin_message = (
    "Добро пожаловать в панель администратора! 🌟"
)


def inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🛍️ Каталог товаров", callback_data="admin_catalog"),
        InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product"),
        InlineKeyboardButton(text="🔍 Поиск", callback_data="admin_search"),
        InlineKeyboardButton(text="📢Рассылка сообщений ",callback_data="send_message")
    )
    return keyboard.adjust(2,2,).as_markup()


@admin_private_router.message(Command("start_admin"))
@admin_private_router.message((F.text.lower().contains('start_admin')) | (F.text.lower() == 'start_admin'))
async def start_cmd(message: types.Message):
    keyboard = inline_keyboard()
    await message.answer_photo(
        photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
        caption=f"{admin_message} \n"
                f"{message.from_user.full_name}! 😊",
        reply_markup=keyboard)


@admin_private_router.callback_query((F.data.startswith('start_admin')))
async def start_command_callback_query(query: types.CallbackQuery) -> None:
    keyboard = inline_keyboard()
    await query.message.edit_caption(
        caption=f"{admin_message}",
        reply_markup=keyboard
    )

