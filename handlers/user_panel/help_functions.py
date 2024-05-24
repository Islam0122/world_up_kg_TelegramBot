from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.config import admin_account
from filter.chat_types import ChatTypeFilter
from aiogram import types, Dispatcher

help_private_router = Router()
help_private_router.message.filter(ChatTypeFilter(['private']))

# Текст помощи для клиентов
help_text_client = (
    f"Список доступных команд:\n"
    f"/start - 🚀 Начать общение\n"
    f"/catalog - 🛍️ Посмотреть каталог товаров\n"
    f"/popular_products - 🚀 Актуальные товары \n"
    f"/search - 🔍 Поиск товаров\n"
    f"/review - ✍️ Оставить отзыв\n"
    f"/about_us - ℹ️ О магазине\n"
    f"/help - 🆘 Получить помощь\n\n"
    f"Если у вас есть вопросы, напишите сюда ({admin_account}), чтобы связаться с администратором."
)

# Текст помощи для администраторов
help_text_admin = (
    f"Список доступных команд для администраторов:\n"
    f"/start - 🚀 Начать общение\n"
    f"/catalog - 🛍️ Посмотреть каталог товаров\n"
    f"/popular_products - 🚀 Актуальные товары \n"
    f"/search - 🔍 Поиск товаров\n"
    f"/review - ✍️ Оставить отзыв\n"
    f"/about_us - ℹ️ О магазине\n"
    f"/help - 🆘 Получить помощь\n"
    f"/start_admin - 🌟 Панель администратора\n"
    f"/add_product - ➕ Добавить товар\n"
    f"/admin_search - 🔍 Поиск товаров для админа\n"
    #"/del - ➖ Удалить товар\n"
    # "/download_database - 💾 Скачать копию базы данных\n"
    # "/info_database - 🌐 База данных\n"
    # "/help - 🆘 Получить помощь\n"
)


def inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="start"),
    )
    return keyboard.adjust().as_markup()


@help_private_router.message((F.text.lower().contains('🆘 Помощь')) | (F.text.lower() == 'help'))
@help_private_router.message(Command("help"))
async def help_command_message(message: types.Message, bot: Bot) -> None:
    if message.from_user.id in bot.my_admins_list:
        await message.answer_photo(photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
                                   caption=help_text_admin,
                                   reply_markup=inline_keyboard())
    else:
        await message.answer_photo(photo=types.FSInputFile('media/images/photo_2024-03-28_06-21-55.jpg'),
                                   caption=help_text_client,
                                   reply_markup=inline_keyboard())


@help_private_router.callback_query(F.data.startswith('help'))
async def help_command_callback_query(query: types.CallbackQuery, bot: Bot) -> None:
    message = query.message
    await message.edit_caption(caption=help_text_client,
                                   reply_markup=inline_keyboard())


