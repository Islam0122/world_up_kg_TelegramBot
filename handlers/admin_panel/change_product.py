from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database.config import group_admin_chat_id, chat_id
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.admin_panel.keyboards import get_sections_keyboard, admin_inline_keyboard, \
    get_categories_clothing_keyboard, get_categories_footwear_keyboard, get_categories_wear_keyboard, \
    get_sizes_clothing_keyboard, get_sizes_footwear_keyboard, get_gender_keyboard
from handlers.user_panel.order_functions import OrderState
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product
from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

add_product_router = Router()
add_product_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,

)


class AddProduct(StatesGroup):
    name = State()
    description = State()
    section = State()
    category = State()
    gender = State()
    size = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        'AddProduct:name': 'Введите название товара 😊:',  #
        'AddProduct:description': 'Введите описание товара 📝:',
        'AddProduct:section': 'Введите раздел товара:',
        'AddProduct:category': 'Введите категорию товара:',
        'AddProduct:size': 'Введите размер товара:',
        'AddProduct:gender': 'Введите пол товара:',
        'AddProduct:price': 'Введите стоимость товара 💰:',
        'AddProduct:image': 'Отправьте изображение товара 🖼️:',
    }


@add_product_router.message(StateFilter("*"), Command("отмена"))
@add_product_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()
    keyboard = ReplyKeyboardRemove()
    await message.answer("🚫 Действие отменено", reply_markup=keyboard)


# Вернутся на шаг назад (на прошлое состояние)
@add_product_router.message(StateFilter("*"), Command("назад"))
@add_product_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == OrderState.Name:
        await message.answer(
            '⏪ Предыдущего шага нет. Чтобы вернуться, введите ФИО или нажмите "Отмена" ⏪')

        return

    previous = None
    for step in OrderState.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"✅ Отлично! Вы вернулись к прошлому шагу:\n{OrderState.texts[previous.state]}",
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


# ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> add  product
@add_product_router.message(StateFilter(None), F.text == "➕ Добавить товар")
@add_product_router.message(StateFilter(None), Command('add_product'))
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("🛍️ Введите название:", reply_markup=keyboard)
    await state.set_state(AddProduct.name)


@add_product_router.callback_query(StateFilter(None), F.data.startswith("add_product"))
async def add_product(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    message = callback.message
    await message.answer("🛍️ Введите название:", reply_markup=keyboard)
    await state.set_state(AddProduct.name)


@add_product_router.message(AddProduct.name, or_f(F.text, F.text == '.'))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if len(message.text) >= 100:
            await message.answer("❌ Название не должно превышать 100 символов. \n Пожалуйста, введите заново.",
                                 reply_markup=keyboard)
            return

        await state.update_data(name=message.text)
    await message.answer("📝 Введите описание:", reply_markup=keyboard)
    await state.set_state(AddProduct.description)


@add_product_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("❌ Вы ввели не допустимые данные для названия. Пожалуйста, введите текст.", )


@add_product_router.message(AddProduct.description, or_f(F.text, F.text == "."))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)
    await message.answer("💬 Отлично! Выберите раздел продукта:", reply_markup=get_sections_keyboard())
    await state.set_state(AddProduct.section)


@add_product_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("❌ Вы ввели недопустимые данные для описания. Пожалуйста, введите текст.")


@add_product_router.message(AddProduct.section, or_f(F.text, F.text == "."))
async def get_section(message: types.Message, state: FSMContext):
    section = message.text.strip().lower()
    if message.text == ".":
        await state.update_data(section=AddProduct.product_for_change.section)
        section = AddProduct.product_for_change.section

    else:
        await state.update_data(section=section)

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


@add_product_router.message(AddProduct.section)
async def get_section2(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")


@add_product_router.message(AddProduct.category, or_f(F.text, F.text == "."))
async def get_category(message: types.Message, state: FSMContext):
    category = message.text.strip().lower()
    if message.text == ".":
        await state.update_data(category=AddProduct.product_for_change.category)
        category = AddProduct.product_for_change.category
    else:
        await state.update_data(category=category)
    # Дальнейшие действия в зависимости от выбранной категории
    if category in ["кофты", "лонгсливы", "футболки", "худи", "куртки", "штаны", "шорты"]:
        await message.answer("Выберите размер:",
                             reply_markup=get_sizes_clothing_keyboard())
        await state.set_state(AddProduct.size)
    elif category in ["кроссовки", "ботинки", "сандалии", "туфли", "сапоги"]:
        await message.answer("Выберите размер:",
                             reply_markup=get_sizes_footwear_keyboard())
        await state.set_state(AddProduct.size)
    elif category in ["электроника", "игрушки", "книги", "спорттовары", "аксессуары"]:
        await state.update_data(size='.')
        await message.answer("Для какого  предназначен товар:",
                             reply_markup=get_gender_keyboard())
        await state.set_state(AddProduct.gender)
    else:
        await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")


@add_product_router.message(AddProduct.category)
async def get_category2(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")


@add_product_router.message(AddProduct.size, or_f(F.text, F.text == "."))
async def get_size(message: types.Message, state: FSMContext):
    size = message.text.strip().lower()
    data = await state.get_data()
    if message.text == ".":
        await state.update_data(size=AddProduct.product_for_change.size)
        size = AddProduct.product_for_change.size

    else:
        await state.update_data(size=size)

    if size in ["xs", "s", "m", "l", "xl", "xxl"] or size in [
        "35", "36", "37", "37,5-38", "38,5-39", "39", "39,5-40", "40", "40-40,5", "40,5-41",
        "41,5-42", "42", "42,5-43", "43", "43-44", "44-45", "45", "45-46", "46", "46-47"
    ]:
        await message.answer("Для какого  предназначен товар:",
                             reply_markup=get_gender_keyboard())
        await state.set_state(AddProduct.gender)

    else:
        await message.answer("Пожалуйста, используйте кнопки на клавиатуре.")


@add_product_router.message(AddProduct.size)
async def get_size2(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")


@add_product_router.message(AddProduct.gender, or_f(F.text, F.text == "."))
async def get_type(message: types.Message, state: FSMContext):
    gender = message.text.strip().lower()
    data = await state.get_data()

    if message.text == ".":
        await state.update_data(gender=AddProduct.product_for_change.gender)
    else:
        await state.update_data(gender=gender)
    if data['category'] in ["электроника", "игрушки", "книги", "спорттовары", "аксессуары"]:
        keyboardфы = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Отмена")],
            ],
            resize_keyboard=True,
        )
        await message.answer("💬 Отлично! Теперь введите стоимость:", reply_markup=keyboardфы)

    else:
        await message.answer("💬 Отлично! Теперь введите стоимость:", reply_markup=keyboard)
    await state.set_state(AddProduct.price)


@add_product_router.message(AddProduct.gender)
async def get_type2(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Пожалуйста, используйте кнопки на клавиатуре.")


@add_product_router.message(AddProduct.price, or_f(F.text, F.text == "."))
async def add_price(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if message.text == ".":
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        await state.update_data(price=message.text)
    if data['category'] in ["электроника", "игрушки", "книги", "спорттовары", "аксессуары"]:
        keyboardфы = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Отмена")],
            ],
            resize_keyboard=True,
        )
        await message.answer("🖼️ Отлично! Теперь загрузите изображение :", reply_markup=keyboardфы)

    else:
        await message.answer("🖼️ Отлично! Теперь загрузите изображение :", reply_markup=keyboard)
    await state.set_state(AddProduct.image)


@add_product_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("❌ Вы ввели недопустимые данные для стоимости. Пожалуйста, введите цену.",
                         )


@add_product_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)

    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Отправьте фото ")
        return
    data = await state.get_data()
    keyboard = ReplyKeyboardRemove()

    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
            if data['section'].lower() == 'другие':
                size_info = ""  # If section is "Другие", size info is not displayed
            else:
                size_info = f"<b>📏 Размер:</b> {data['size']}\n"

                # Construct the message text
            text = (
                "<b>📦 товар изменен !</b>\n"
                f"<b>🏷 Название:</b> {data['name']}\n"
                f"<b>📝 Описание:</b> {data['description']}\n"
                f"<b>🔍 Раздел:</b> {data['section']}\n"
                f"<b>📦 Категория:</b> {data['category']}\n"
                f"<b>👤 Пол:</b> {data['gender']}\n"
                f"{size_info}"  # Insert size information if available
                f"<b>💰 Цена:</b> {data['price']}\n\n"
            )

            # Send the notification to the admin group chat
            await bot.send_photo(group_admin_chat_id, data['image'], caption=text)

            # Notify the user of the successful operation
            await message.answer("✅ Успешно изменен!", reply_markup=keyboard)
        else:
            await orm_add_product(session, data)

            if data['section'].lower() == 'другие':
                size_info = ""  # If section is "Другие", size info is not displayed
            else:
                size_info = f"<b>📏 Размер:</b> {data['size']}\n"

                # Construct the message text
            text = (
                "<b>📦 Новый продукт добавлен в каталог!</b>\n"
                f"<b>🏷 Название:</b> {data['name']}\n"
                f"<b>📝 Описание:</b> {data['description']}\n"
                f"<b>🔍 Раздел:</b> {data['section']}\n"
                f"<b>📦 Категория:</b> {data['category']}\n"
                f"<b>👤 Пол:</b> {data['gender']}\n"
                f"{size_info}"  # Insert size information if available
                f"<b>💰 Цена:</b> {data['price']}\n\n"
            )

            # Send the notification to the admin group chat
            await bot.send_photo(group_admin_chat_id, data['image'], caption=text)
            # Send the notification to the user chat
            await bot.send_photo(chat_id, data['image'], caption=text)

            # Notify the user of the successful operation
            await message.answer("✅ Успешно добавлен!", reply_markup=keyboard)

        await state.clear()
    except Exception as e:
        print(e)
        await state.clear()

    AddProduct.product_for_change = None


@add_product_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("❌ Ошибка при загрузке изображения. Пожалуйста, отправьте изображение.")


# -------------------------> Del product <-------------------------------------------------------------
@add_product_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    await callback.answer("✅ Успешно удален")
    await callback.message.answer("✅ Успешно Удален !!!")


# -------------------------------> END <--------------------------------------------------------------
# --------------------------------------------> Edit product <--------------------------------------
@add_product_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    product_for_change = await orm_get_product(session, int(product_id))
    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Пожалуйста, введите новое название товара", reply_markup=keyboard
    )
    await callback.message.answer(
        "Вы можете пропустить шаги, вводя точки (.) 😊"
    )
    await state.set_state(AddProduct.name)

# -------------------------------> END <--------------------------------------------------------------
