from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database.config import group_admin_chat_id
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.admin_panel.keyboards import get_sections_keyboard, admin_inline_keyboard, \
    get_categories_clothing_keyboard, get_categories_footwear_keyboard, get_categories_wear_keyboard, \
    get_sizes_clothing_keyboard, get_sizes_footwear_keyboard, get_gender_keyboard
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product
from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="отмена")],
        [KeyboardButton(text="назад")],
    ],
    resize_keyboard=True,

)
# Определение состояний FSM
class OrderState(StatesGroup):
    Product = State()
    Name = State()
    PhoneNumber = State()
    Email = State()
    Address = State()
    product_for_change = None
    texts = {
        'OrderState:Name': 'Введите ваше ФИО 😊:',
        'OrderState:PhoneNumber': 'Введите ваш номер телефона 📞:',
        'OrderState:Email': 'Введите ваш адрес электронной почты ✉️:',
        'OrderState:Address': 'Введите ваш адрес  🏠:',
    }


order_router = Router()
order_router.message.filter(ChatTypeFilter(["private"]))


@order_router.callback_query(StateFilter(None), F.data.startswith("buy_"))
async def order_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    print(product_id)
    message = callback.message
    if message:
        await message.answer(
            f"Вы выбрали товар с ID {product_id}. Для оформления заказа, пожалуйста, укажите ваше ФИО:",reply_markup=keyboard)
        await state.update_data(product_id=product_id)
        await state.set_state(OrderState.Name)

    else:
        await message.answer("⚠️ Пожалуйста, введите корректную информацию.")


# Обработчики для сбора информации о пользователе и оформлении заказа
@order_router.message(OrderState.Name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text:
        await message.answer("Теперь укажите ваш номер телефона:")
        await state.update_data(name=message.text)
        await state.set_state(OrderState.PhoneNumber)
    else:
        await message.answer("⚠️ Пожалуйста, введите корректную информацию.")


@order_router.message(OrderState.PhoneNumber)
async def process_phone_number(message: types.Message, state: FSMContext):
    if message.text:
        # Проверка на корректность ввода номера телефона
        if message.text:
            await state.update_data(phone_number=message.text)
            await message.answer("Теперь укажите вашу электронную почту:")
            await state.set_state(OrderState.Email)
        else:
            await message.answer("⚠️ Пожалуйста, введите корректный номер телефона (цифр без пробелов и символов).")
    else:
        await message.answer("⚠️ Пожалуйста, введите корректную информацию.")



@order_router.message(OrderState.Email)
async def process_email(message: types.Message, state: FSMContext):
    if message.text:
        # Проверка на корректность ввода электронной почты (можно использовать более сложную логику)
        if message.text :
            await state.update_data(email=message.text)
            await message.answer("Теперь укажите ваш адрес:")
            await state.set_state(OrderState.Address)
        else:
            await message.answer("⚠️ Пожалуйста, введите корректный адрес электронной почты.")
    else:
        await message.answer("⚠️ Пожалуйста, введите корректную информацию.")


@order_router.message(OrderState.Address)
async def process_address(message: types.Message, state: FSMContext, bot: Bot, session: AsyncSession):
    keyboard = ReplyKeyboardRemove()
    data = await state.get_data()  # Получаем данные из состояния
    if message.text:
        user_info = f"{message.from_user.first_name}"
        if message.from_user.last_name:
            user_info += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"
        product = await orm_get_product(session,data.get('product_id'))
        if product.section.lower() == 'другие':  # Check for lowercase 'другие'
            size_info = ""  # Если раздел "Другие", размер не выводится
        else:
            size_info = f"<b>📏 Размер:</b> {product.size}\n"
        text = (
            f"<b>🆔 ID:</b> {product.id}\n"
            f"<b>🏷 Название:</b> {product.name}\n"
            f"<b>📝 Описание:</b> {product.description}\n"
            f"<b>🔍 Раздел:</b> {product.section}\n"
            f"<b>📦 Категория:</b> {product.category}\n"
            f"<b>👤 Пол :</b> {product.gender}\n"
            f"{size_info}"  # Вставляем информацию о размере
            f"<b>💰 Цена:</b> {product.price}\n\n"
            f"Новый заказ от {user_info}:\n" \
            f"Имя: {data.get('name')}\n" \
            f"Телефон: {data.get('phone_number')}\n" \
            f"Email: {data.get('email')}\n" \
            f"Адрес: {message.text}\n" \
            f"Пожалуйста, свяжитесь с пользователем для уточнения деталей."
        )

        # Отправляем уведомление администратору
        await bot.send_photo(group_admin_chat_id,product.image,caption= text)
        await message.answer("Спасибо за предоставленную информацию! Ваш запрос успешно принят и будет обработан. 😊")
        await message.answer("Админ с вами свяжется в ближайшее время! 📞", reply_markup=keyboard)
        await state.clear()  # Очищаем состояние
    else:
        await message.answer("⚠️ Пожалуйста, введите корректную информацию.")

