from aiogram import F, types, Router, Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from database.config import users
from filter.chat_types import ChatTypeFilter

# Create router for private chats
user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

# Define messages in different languages
messages = {
    'ru': {
        'welcome': "Рады видеть вас в нашем магазине! 😊\n\nМы предлагаем широкий выбор товаров по доступным ценам.\nВыбирайте из нашего каталога или воспользуйтесь поиском.\n\nНадеемся, что вы найдете у нас то, что искали.\nСвяжитесь с нами, если у вас возникнут вопросы.",
        'catalog': "🛍️ Каталог товаров",
        'search': "🔍 Поиск товаров",
        'popular_products': "🚀 Популярные товары",
        'review': "✍️ Оставить отзыв",
        'help': "🆘 Помощь",
        'about_us': "ℹ️ О магазине",
        'our_channel': "📢 Наш канал",
        'our_instagram': "📷 Наш Instagram",
        'select_language': "🌐 Выбрать язык"
    },
    'en': {
        'welcome': "We are glad to see you in our store! 😊\n\nWe offer a wide range of products at affordable prices.\nChoose from our catalog or use the search.\n\nWe hope you find what you were looking for.\nContact us if you have any questions.",
        'catalog': "🛍️ Product Catalog",
        'search': "🔍 Product Search",
        'popular_products': "🚀 Popular Products",
        'review': "✍️ Leave a Review",
        'help': "🆘 Help",
        'about_us': "ℹ️ About Us",
        'our_channel': "📢 Our Channel",
        'our_instagram': "📷 Our Instagram",
        'select_language': "🌐 Select Language"
    }
}

# External dictionary to store user preferences (could be a database in a real application)
user_preferences = {}

def create_inline_keyboard(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['catalog'], callback_data="catalog"),
        InlineKeyboardButton(text=messages[language]['search'], callback_data="search"),
        InlineKeyboardButton(text=messages[language]['popular_products'], callback_data="popular_products"),
        InlineKeyboardButton(text=messages[language]['review'], callback_data="review"),
        InlineKeyboardButton(text=messages[language]['help'], callback_data="help"),
        InlineKeyboardButton(text=messages[language]['about_us'], callback_data="about_us"),
        InlineKeyboardButton(text=messages[language]['our_channel'], url="https://t.me/WourldUpKg"),
        InlineKeyboardButton(text=messages[language]['our_instagram'], url="https://www.instagram.com/world_up_kg?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw=="),
        InlineKeyboardButton(text=messages[language]['select_language'], callback_data="select_language")
    )
    return keyboard.adjust(3, 3, 2).as_markup()

@user_private_router.message(CommandStart())
@user_private_router.message(F.text.lower().contains('start') | (F.text.lower() == 'start'))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}
    language = user_preferences[user_id]['language']
    keyboard = create_inline_keyboard(language)
    await message.answer_photo(
        photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
        caption=f" {message.from_user.full_name}! 😊\n\n{messages[language]['welcome']}",
        reply_markup=keyboard
    )

@user_private_router.callback_query(F.data.startswith('start'))
async def start_command_callback_query(query: types.CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_id not in users:
        users.append(user_id)
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}
    language = user_preferences[user_id]['language']
    keyboard = create_inline_keyboard(language)
    await query.message.answer_photo(
        photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
        caption=f"{query.from_user.full_name}! 😊\n\n{messages[language]['welcome']}",
        reply_markup=keyboard
    )

@user_private_router.message(F.text.lower().contains("language"))
async def select_language(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_language_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_language_en")
    )
    await message.answer("Please select your language / Пожалуйста, выберите язык:", reply_markup=keyboard.adjust(2).as_markup())

@user_private_router.callback_query(F.data.startswith('set_language_'))
async def set_language_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in users:
        users.append(user_id)

    if user_id not in user_preferences:
        user_preferences[user_id] = {}

    if query.data == "set_language_ru":
        user_preferences[user_id]['language'] = 'ru'
        response = "Язык установлен на русский."
    elif query.data == "set_language_en":
        user_preferences[user_id]['language'] = 'en'
        response = "Language set to English."

    await query.message.answer(response)

@user_private_router.callback_query(F.data == 'select_language')
async def select_language_callback(query: types.CallbackQuery):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_language_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_language_en")
    )
    await query.message.answer("Please select your language / Пожалуйста, выберите язык:", reply_markup=keyboard.adjust(2).as_markup())
