from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database.config import group_admin_chat_id, chat_id, admin_account
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.admin_panel.change_product import AddProduct, cancel_messages, keyboard
from handlers.admin_panel.keyboards import get_sections_keyboard, admin_inline_keyboard, \
    get_categories_clothing_keyboard, get_categories_footwear_keyboard, get_categories_wear_keyboard, \
    get_sizes_clothing_keyboard, get_sizes_footwear_keyboard, get_gender_keyboard, get_gender_gen_keyboard
from handlers.user_panel.order_functions import OrderState, texts
from handlers.user_panel.start_functions import user_preferences
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product
from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

from handlers.user_panel.start_functions import user_preferences

unknown_private_router = Router()
unknown_private_router.message.filter(ChatTypeFilter(['private']))

@unknown_private_router.message(StateFilter("*"), Command("отмена"))
@unknown_private_router.message(StateFilter("*"), F.text.casefold() == "отмена")
@unknown_private_router.message(StateFilter("*"), Command("отмена"))
@unknown_private_router.message(StateFilter("*"), Command("cancel"))
@unknown_private_router.message(StateFilter("*"), F.text.casefold()== 'cancel')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await message.answer(cancel_messages[language], reply_markup=ReplyKeyboardRemove())
    await state.clear()



# Вернутся на шаг назад (на прошлое состояние)
@unknown_private_router.message(StateFilter("*"), Command("назад"))
@unknown_private_router.message(StateFilter("*"), F.text.casefold() == "назад")
@unknown_private_router.message(StateFilter("*"), Command("back"))
@unknown_private_router.message(StateFilter("*"), F.text.casefold()== 'back')
async def back_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    data = await state.get_data()
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    if current_state == OrderState.Name:
            await message.answer(texts[language]['no_previous_step'])
            return

    previous = None
    for step in OrderState.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"{texts[language]['back_to_previous_step']}\n"
                f"{texts[language][f'OrderState:{previous.state.split(':')[1]}']}",
            )
            return
        previous = step
    if current_state == AddProduct.name:
        await message.answer(
            '⏪ Предыдущего шага нет. Чтобы вернуться, введите название или нажмите "Отмена" ⏪')
        await state.set_state(AddProduct.name)
    if current_state == AddProduct.description:
        await message.answer(
            '✅ Отлично! Вы вернулись к прошлому шагу :🛍️ Введите название:')
        await state.set_state(AddProduct.name)
    if current_state == AddProduct.section:
        await message.answer("✅ Отлично! Вы вернулись к прошлому шагу:📝 Введите описание:", reply_markup=keyboard)
        await state.set_state(AddProduct.description)
    if current_state == AddProduct.category:
        await message.answer("✅ Отлично! Вы вернулись к прошлому шагу: Выберите раздел продукта:",
                             reply_markup=get_sections_keyboard())
        await state.set_state(AddProduct.section)
    if current_state == AddProduct.size:
        section = data['section']
        if section == "одежда":
            await message.answer("Выберите категорию одежды:", reply_markup=get_categories_clothing_keyboard())
            await state.set_state(AddProduct.category)
        elif section == "обувь":
            await message.answer("Выберите категорию обуви:", reply_markup=get_categories_footwear_keyboard())
            await state.set_state(AddProduct.category)
        elif section == "другие":
            await message.answer(
                "Выберите категорию товаров из раздела Другие: ", reply_markup=get_categories_wear_keyboard())
            await state.set_state(AddProduct.category)
        else:
            await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")
    if current_state == AddProduct.gender:
        category = data['category']
        if category in ["кофты", "лонгсливы", "футболки", "худи", "куртки", "штаны", "шорты"]:
            await message.answer("Выберите размер:",
                                 reply_markup=get_sizes_clothing_keyboard())
            await state.set_state(AddProduct.size)
        elif category in ["кроссовки", "ботинки", "сандалии", "туфли", "сапоги"]:
            await message.answer("Выберите размер:",
                                 reply_markup=get_sizes_footwear_keyboard())
            await state.set_state(AddProduct.size)

        else:
            await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")
    if current_state == AddProduct.price:
        await message.answer("Для какого  предназначен товар:",
                             reply_markup=get_gender_keyboard())
        await state.set_state(AddProduct.gender)
    if current_state == AddProduct.image:
        await message.answer("💬 Отлично! Теперь введите стоимость:", reply_markup=keyboard)
        await state.set_state(AddProduct.price)

unknown_2private_router = Router()
unknown_2private_router.message.filter(ChatTypeFilter(['private']))
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

# External dictionary to store user preferences (could be a database in a real application)
# Handler for unknown commands
@unknown_2private_router.message()
async def unknown_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_preferences:
        user_preferences[user_id] = {'language': 'ru'}  # Default language is Russian

    language = user_preferences[user_id]['language']
    response_message = messages[language]['unknown_command']

    await message.reply(response_message, parse_mode="Markdown")
