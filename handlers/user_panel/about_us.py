from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.config import admin_account
from filter.chat_types import ChatTypeFilter
from aiogram import types, Dispatcher

about_private_router = Router()
about_private_router.message.filter(ChatTypeFilter(['private']))

# Текст о магазине
about_text = (
    "🌟 Добро пожаловать в мир стиля с World_up_kg! 🌟\n\n👗👟 Присоединяйтесь к нашему телешопу, где стиль и "
    "комфорт встречаются. Мы гордимся широким ассортиментом стильной одежды и качественной обуви для всех "
    "возрастов и предпочтений.\n\n🛍️ Наш телешрам-бот поможет вам подобрать идеальный наряд или аксессуары, "
    "а наши алгоритмы предложат персонализированные рекомендации, учитывая ваш стиль и предпочтения.\n\n📦 Мы "
    "ценим ваше время, поэтому гарантируем быструю и надежную доставку прямо к вашему порогу.\n\n💬 Наша команда "
    "доступна 24/7, чтобы ответить на все ваши вопросы и помочь вам с выбором.\n\nПрисоединяйтесь к нашему "
    "телешопу уже сегодня и окунитесь в мир стиля с World_up_kg! 💫"
)

# Контактная информация
contacts_text = (
    "📞 Телефон: +123456789\n"
    "📧 Email: example@example.com\n"
    "🌐 Веб-сайт: [Название вашего сайта](http://www.example.com)\n"
    "🏢 Адрес: ул. Примерная, д. 123, г. Примерный\n"
)


def inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="start"),
    )
    return keyboard.adjust().as_markup()


@about_private_router.message((F.text.lower().contains('ℹ️ О магазине')) | (F.text.lower() == 'about_us'))
@about_private_router.message(Command("about_us"))
async def about_us_command_message(message: types.Message) -> None:
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption=f"{about_text}\n\n{contacts_text}",
        reply_markup=inline_keyboard()
    )


@about_private_router.callback_query(F.data.startswith('about_us'))
async def about_us_command_callback_query(query: types.CallbackQuery, bot: Bot) -> None:
    await query.message.edit_caption(
        caption=f"{about_text}\n\n{contacts_text}",
        reply_markup=inline_keyboard()
    )
