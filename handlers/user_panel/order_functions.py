from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import group_admin_chat_id
from filter.chat_types import ChatTypeFilter
from handlers.admin_panel.keyboards import get_sections_keyboard, admin_inline_keyboard, \
    get_categories_clothing_keyboard, get_categories_footwear_keyboard, get_categories_wear_keyboard, \
    get_sizes_clothing_keyboard, get_sizes_footwear_keyboard, get_gender_keyboard
from handlers.user_panel.start_functions import user_preferences
from keyboard_list.reply import get_keyboard
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product
from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

# Define language-specific messages
texts = {
    'ru': {
        'OrderState:Name': 'Введите ваше ФИО 😊:',
        'OrderState:PhoneNumber': 'Введите ваш номер телефона 📞:',
        'OrderState:Email': 'Введите ваш адрес электронной почты ✉️:',
        'OrderState:Address': 'Введите ваш адрес  🏠:',
        'cancel': 'отмена',
        'back': 'назад',
        'action_cancelled': "🚫 Действие отменено",
        'order_confirmation': "Спасибо за предоставленную информацию! Ваш запрос успешно принят и будет обработан. 😊",
        'admin_contact': "Админ с вами свяжется в ближайшее время! 📞",
        'invalid_info': "⚠️ Пожалуйста, введите корректную информацию.",
        'invalid_phone': "⚠️ Пожалуйста, введите корректный номер телефона (цифры без пробелов и символов).",
        'invalid_email': "⚠️ Пожалуйста, введите корректный адрес электронной почты.",
        'no_previous_step': '⏪ Предыдущего шага нет. Чтобы вернуться, введите ФИО или нажмите "Отмена" ⏪',
        'back_to_previous_step': '✅ Отлично! Вы вернулись к прошлому шагу:',
                                 'order_product_chosen': 'Вы выбрали товар с ID {product_id}. Для оформления заказа, пожалуйста, укажите ваше ФИО:'

},
    'en': {
        'OrderState:Name': 'Enter your full name 😊:',
        'OrderState:PhoneNumber': 'Enter your phone number 📞:',
        'OrderState:Email': 'Enter your email address ✉️:',
        'OrderState:Address': 'Enter your address 🏠:',
        'cancel': 'cancel',
        'back': 'back',
        'action_cancelled': "🚫 Action cancelled",
        'order_confirmation': "Thank you for the information provided! Your request has been successfully received and will be processed. 😊",
        'admin_contact': "The admin will contact you soon! 📞",
        'invalid_info': "⚠️ Please provide valid information.",
        'invalid_phone': "⚠️ Please enter a valid phone number (digits without spaces and symbols).",
        'invalid_email': "⚠️ Please enter a valid email address.",
        'no_previous_step': '⏪ No previous step. To go back, enter your full name or click "Cancel" ⏪',
        'back_to_previous_step': '✅ Great! You have returned to the previous step:',
        'order_product_chosen': 'You have chosen a product with ID {product_id}. To place an order, please provide your full name:'

    }
}



# Generate the keyboard based on the user's language preference
def get_keyboard(language):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts[language]['cancel'])],
            [KeyboardButton(text=texts[language]['back'])]
        ],
        resize_keyboard=True
    )


# Define FSM states
class OrderState(StatesGroup):
    Product = State()
    Name = State()
    PhoneNumber = State()
    Email = State()
    Address = State()


# Define the router for handling order messages
order_router = Router()
order_router.message.filter(ChatTypeFilter(["private"]))


# Handler for starting the order process
@order_router.callback_query(StateFilter(None), F.data.startswith("buy_"))
async def order_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    message = callback.message
    user_id = callback.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')  # Get user's language preference

    if message:
        await message.answer(
            texts[language]['order_product_chosen'].format(product_id=product_id),
            reply_markup=get_keyboard(language)
        )
        await state.update_data(product_id=product_id)
        await state.set_state(OrderState.Name)
    else:
        await message.answer(texts[language]['invalid_info'])


# Handlers for collecting user information and completing the order
@order_router.message(OrderState.Name)
async def process_name(message: types.Message, state: FSMContext):
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')
    if message.text:
        await message.answer(texts[language]['OrderState:PhoneNumber'],reply_markup=get_keyboard(language))
        await state.update_data(name=message.text)
        await state.set_state(OrderState.PhoneNumber)
    else:
        await message.answer(texts[language]['invalid_info'])


@order_router.message(OrderState.PhoneNumber)
async def process_phone_number(message: types.Message, state: FSMContext):
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')
    if message.text:
        # Add phone number validation logic if needed
        await state.update_data(phone_number=message.text)
        await message.answer(texts[language]['OrderState:Email'])
        await state.set_state(OrderState.Email)
    else:
        await message.answer(texts[language]['invalid_phone'])


@order_router.message(OrderState.Email)
async def process_email(message: types.Message, state: FSMContext):
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')
    if message.text:
        # Add email validation logic if needed
        await state.update_data(email=message.text)
        await message.answer(texts[language]['OrderState:Address'])
        await state.set_state(OrderState.Address)
    else:
        await message.answer(texts[language]['invalid_email'])


@order_router.message(OrderState.Address)
async def process_address(message: types.Message, state: FSMContext, bot: Bot, session: AsyncSession):
    keyboard = ReplyKeyboardRemove()
    data = await state.get_data()  # Get data from state
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')
    if message.text:
        user_info = f"{message.from_user.first_name}"
        if message.from_user.last_name:
            user_info += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"

        product = await orm_get_product(session, data.get('product_id'))
        if product.section.lower() == 'другие':  # Check for lowercase 'другие'
            size_info = ""  # If the section is "Другие", size is not displayed
        else:
            size_info = f"<b>📏 Размер:</b> {product.size}\n"
        text = (
            f"<b>🆔 ID:</b> {product.id}\n"
            f"<b>🏷 Название:</b> {product.name}\n"
            f"<b>📝 Описание:</b> {product.description}\n"
            f"<b>🔍 Раздел:</b> {product.section}\n"
            f"<b>📦 Категория:</b> {product.category}\n"
            f"<b>👤 Пол :</b> {product.gender}\n"
            f"{size_info}"  # Insert size information
            f"<b>💰 Цена:</b> {product.price}\n\n"
            f"Новый заказ от {user_info}:\n"
            f"Имя: {data.get('name')}\n"
            f"Телефон: {data.get('phone_number')}\n"
            f"Email: {data.get('email')}\n"
            f"Адрес: {message.text}\n"
            f"Пожалуйста, свяжитесь с пользователем для уточнения деталей."
        )
        photos = [
            product.image1,
            product.image2,
            product.image3,
            product.image4,
        ]
        media = [
            types.InputMediaPhoto(media=photo_id, caption=text)
            for photo_id in photos
        ]

        # Send notification to the admin
        await bot.send_media_group(group_admin_chat_id, media=media, )
        await bot.send_message(group_admin_chat_id, text=text)
        await message.answer(texts[language]['order_confirmation'])
        await message.answer(texts[language]['admin_contact'], reply_markup=keyboard)
        await state.clear()  # Clear the state
    else:
        await message.answer(texts[language]['invalid_info'])


# Handler for cancelling the order process
@order_router.message(StateFilter("*"), Command("отмена"))
@order_router.message(StateFilter("*"), Command("cancel"))
@order_router.message(StateFilter("*"), F.text.lower().isin(['отмена', 'cancel']))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    await state.clear()
    await message.answer(texts[language]['action_cancelled'], reply_markup=ReplyKeyboardRemove())