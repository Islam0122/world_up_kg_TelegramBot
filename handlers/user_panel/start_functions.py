from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.config import users
from filter.chat_types import ChatTypeFilter
from keyboard_list.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

# Приветственное сообщение
welcome_message = (
    "Рады видеть вас в нашем магазине! 😊\n\n"
    "Мы предлагаем широкий выбор товаров по доступным ценам.\n"
    "Выбирайте из нашего каталога или воспользуйтесь поиском.\n\n"
    "Надеемся, что вы найдете у нас то, что искали.\n"
    "Свяжитесь с нами, если у вас возникнут вопросы."
)


def create_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🛍️ Каталог товаров", callback_data="catalog"),
        InlineKeyboardButton(text="🔍 Поиск товаров", callback_data="search"),
        InlineKeyboardButton(text="🚀 Актуальные товары", callback_data="popular_products"),
        InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data="review"),  # Новая кнопка для отзыва
        InlineKeyboardButton(text="🆘 Помощь", callback_data="help"),
        InlineKeyboardButton(text="ℹ️ О магазине", callback_data="about_us")
    )
    return keyboard.adjust(3,).as_markup()


@user_private_router.message(CommandStart())
@user_private_router.message((F.text.lower().contains('start')) | (F.text.lower() == 'start'))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
    keyboard = create_inline_keyboard()
    await message.answer_photo(
        photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
        caption=f"Добро пожаловать в наш магазин, {message.from_user.full_name}! 😊\n\n{welcome_message}",
        reply_markup=keyboard
    )


@user_private_router.callback_query((F.data.startswith('start')))
async def start_command_callback_query(query: types.CallbackQuery) -> None:
    message= query.message
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
    keyboard = create_inline_keyboard()
    await message.answer_photo(
        photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
        caption=f"Добро пожаловать в наш магазин, {message.from_user.full_name}! 😊\n\n{welcome_message}",
        reply_markup=keyboard
    )