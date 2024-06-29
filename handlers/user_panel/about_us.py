from aiogram import F, types, Router, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filter.chat_types import ChatTypeFilter
from handlers.user_panel.help_functions import inline_keyboard
from handlers.user_panel.start_functions import user_preferences

about_private_router = Router()
about_private_router.message.filter(ChatTypeFilter(['private']))

# English and Russian versions of the about text and contacts
about_texts = {
    'ru': {
        'about': (
            "🌟 Добро пожаловать в мир стиля с World_up_kg! 🌟\n\n👗👟 Присоединяйтесь к нашему телешопу, где стиль и "
            "комфорт встречаются. Мы гордимся широким ассортиментом стильной одежды и качественной обуви для всех "
            "возрастов и предпочтений.\n\n🛍️ Наш телешрам-бот поможет вам подобрать идеальный наряд или аксессуары, "
            "а наши алгоритмы предложат персонализированные рекомендации, учитывая ваш стиль и предпочтения.\n\n📦 Мы "
            "ценим ваше время, поэтому гарантируем быструю и надежную доставку прямо к вашему порогу.\n\n💬 Наша команда "
            "доступна 24/7, чтобы ответить на все ваши вопросы и помочь вам с выбором.\n\nПрисоединяйтесь к нашему "
            "телешопу уже сегодня и окунитесь в мир стиля с World_up_kg! 💫"
        ),
        'contacts': (
            "📞 Телефон: +123456789\n"
            "📧 Email: Koshelev.sk@gmail.com\n"
            "🏢 Адрес: ул. Примерная, д. 123, г. Примерный\n"
        )
    },
    'en': {
        'about': (
            "🌟 Welcome to the world of style with World_up_kg! 🌟\n\n👗👟 Join our tele-shop where style and "
            "comfort meet. We take pride in offering a wide range of stylish clothing and quality footwear for all "
            "ages and preferences.\n\n🛍️ Our tele-shop bot will help you find the perfect outfit or accessories, "
            "and our algorithms will provide personalized recommendations based on your style and preferences.\n\n📦 We "
            "value your time, so we guarantee fast and reliable delivery right to your doorstep.\n\n💬 Our team is "
            "available 24/7 to answer all your questions and assist you with your choices.\n\nJoin our tele-shop "
            "today and immerse yourself in the world of style with World_up_kg! 💫"
        ),
        'contacts': (
            "📞 Phone: +123456789\n"
            "📧 Email: Koshelev.sk@gmail.com\n"
            "🏢 Address: 123 Example St, Example City\n"
        )
    }
}


@about_private_router.message((F.text.lower().contains('ℹ️ О магазине')) | (F.text.lower() == 'about_us'))
@about_private_router.message(Command("about_us"))
async def about_us_command_message(message: types.Message) -> None:
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption=f"{about_texts[language]['about']}\n\n{about_texts[language]['contacts']}",
        reply_markup=inline_keyboard(language)
    )


@about_private_router.callback_query(F.data.startswith('about_us'))
async def about_us_command_callback_query(query: types.CallbackQuery, bot: Bot) -> None:
    user_id = query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    await query.message.edit_caption(
        caption=f"{about_texts[language]['about']}\n\n{about_texts[language]['contacts']}",
        reply_markup=inline_keyboard(language)
    )