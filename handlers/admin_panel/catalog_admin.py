from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from filter.chat_types import ChatTypeFilter, IsAdmin
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product

from database.orm_query import orm_get_products
from keyboard_list.inline import *
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder



def get_sections_keyboard():
    keyboard = InlineKeyboardBuilder() # Add row_width to organize buttons in a single column
    keyboard.add(
        InlineKeyboardButton(text="Одежда", callback_data="section_Одежда"),
        InlineKeyboardButton(text="Обувь", callback_data="section_Обувь"),
        InlineKeyboardButton(text="Другие", callback_data="section_Другие"),
    )
    return keyboard.adjust().as_markup()

def get_categories_keyboard(section):
    keyboard =  InlineKeyboardBuilder()
    if section == "одежда" or section == "Одежда":
        keyboard.add(
            InlineKeyboardButton(text="Кофты", callback_data="category_кофты"),  # Outerwear
            InlineKeyboardButton(text="Лонгсливы", callback_data="category_лонгсливы"),  # Long sleeves
            InlineKeyboardButton(text="Худи", callback_data="category_худи"),  # Hoodies
            InlineKeyboardButton(text="Футболки", callback_data="category_футболки"),  # T-shirts
            InlineKeyboardButton(text="Штаны", callback_data="category_штаны"),  # Pants
            InlineKeyboardButton(text="Куртки", callback_data="category_куртки"),  # Jackets
            InlineKeyboardButton(text="Шорты", callback_data="category_шорты"),  # Shorts
        )

    elif section == "Обувь" or section == "обувь":
        keyboard.add(
            InlineKeyboardButton(text="Кроссовки", callback_data="category_кроссовки"),
            InlineKeyboardButton(text="Ботинки", callback_data="category_ботинки"),
            InlineKeyboardButton(text="Сандалии", callback_data="category_сандалии"),
            InlineKeyboardButton(text="Туфли", callback_data="category_туфли"),
            InlineKeyboardButton(text="Сапоги", callback_data="category_сапоги"),
        )
    else:
        keyboard.add(
            InlineKeyboardButton(text="Электроника", callback_data="category_электроника"),
            InlineKeyboardButton(text="Книги", callback_data="category_книги"),
            InlineKeyboardButton(text="Аксессуары", callback_data="category_аксессуары"),
            InlineKeyboardButton(text="Игрушки", callback_data="category_игрушки"),
            InlineKeyboardButton(text="Спорттовары", callback_data="category_спорттовары"),

        )

    return keyboard.adjust(3,3).as_markup()

def get_sizes_keyboard(section):
    keyboard = InlineKeyboardBuilder()
    if section == "одежда" or section == "Одежда":
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        for size in sizes:
            keyboard.add(InlineKeyboardButton(text=size, callback_data=f"size_{size}"))
    else:
        sizes = ["35", "36", "37", "37,5-38", "38,5-39", "39", "39,5-40", "40", "40-40,5", "40,5-41",
         "41,5-42", "42", "42,5-43", "43", "43-44", "44-45", "45", "45-46", "46", "46-47"]
        for size in sizes:
              keyboard.add(InlineKeyboardButton(text=size, callback_data=f"size_{size}"))
    return keyboard.adjust(5, 5).as_markup()

def get_genders_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Мужской", callback_data="gender_Мужской"),
        InlineKeyboardButton(text="Женская", callback_data="gender_Женская"),
        InlineKeyboardButton(text="Для всех", callback_data="gender_Для всех")
    )
    return keyboard.adjust(3,3).as_markup()
catalog_admin_router = Router()
catalog_admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


class AdminCatalogFilters(StatesGroup):
    SECTION = State()
    CATEGORY = State()
    SIZE = State()
    GENDER = State()


def filter_products(products, filters):
    filtered_products = []
    for product in products:
        if (filters.get('size', 'any') == 'any' or product.size.lower() == filters['size'].lower()) and \
                (filters.get('section', 'any') == 'any' or product.section.lower() == filters['section'].lower()) and \
                (filters.get('category', 'any') == 'any' or product.category.lower() == filters['category'].lower()) and \
                (filters.get('gender', 'any') == 'any' or product.gender.lower() == filters['gender'].lower()):
            filtered_products.append(product)
    return filtered_products


@catalog_admin_router.message(F.text.lower() == "🛍️ Каталог товаров")
@catalog_admin_router.message(Command("catalog_admin"))
async def start_catalog_filtering(message: types.Message, state: FSMContext):
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption="Выберите раздел, в котором вы ищете товар:",
        parse_mode="HTML",
        reply_markup=get_sections_keyboard()
    )

    await state.set_state(AdminCatalogFilters.SECTION)


@catalog_admin_router.callback_query((F.data.startswith("admin_catalog")))
async def start_catalog_filtering(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption="Выберите раздел, в котором вы ищете товар:",
        parse_mode="HTML",
        reply_markup=get_sections_keyboard()
    )

    await state.set_state(AdminCatalogFilters.SECTION)


@catalog_admin_router.callback_query(AdminCatalogFilters.SECTION, F.data.startswith("section_"))
async def process_section_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()

    selected_section = callback_query.data.split('_')[1]

    await state.update_data(section=selected_section)
    await state.set_state(AdminCatalogFilters.CATEGORY)
    data = await state.get_data()
    await callback_query.message.answer("Выберите категорию товара:",
                                        reply_markup=get_categories_keyboard(data['section']))


@catalog_admin_router.callback_query(AdminCatalogFilters.CATEGORY, F.data.startswith("category_"))
async def process_category_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    selected_category = callback_query.data.split('_')[1]
    await state.update_data(category=selected_category)
    await state.set_state(AdminCatalogFilters.CATEGORY)
    data = await state.get_data()
    if data['section'] == 'другие' or data['section'] == 'Другие':
        await state.set_state(AdminCatalogFilters.GENDER)
        await callback_query.message.answer("Выберите тип товара:", reply_markup=get_genders_keyboard())
    else:
        await state.set_state(AdminCatalogFilters.SIZE)
        await callback_query.message.answer("Выберите размер товара:", reply_markup=get_sizes_keyboard(data['section']))


@catalog_admin_router.callback_query(AdminCatalogFilters.SIZE, F.data.startswith("size_"))
async def process_size_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    selected_size = callback_query.data.split('_')[1]
    await state.update_data(size=selected_size)
    await state.set_state(AdminCatalogFilters.GENDER)
    await callback_query.message.answer("Выберите пол товара:", reply_markup=get_genders_keyboard())


@catalog_admin_router.callback_query(AdminCatalogFilters.GENDER, F.data.startswith("gender_"))
async def process_gender_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    selected_gender = callback_query.data.split('_')[1]
    await state.update_data(gender=selected_gender)
    message = callback_query.message
    data = await state.get_data()
    keyboard = ReplyKeyboardRemove()
    try:
        products = await orm_get_products(session)
    except Exception as e:
        await message.answer(f"An error occurred while fetching products: {e}")
        return

    filtered_products = filter_products(products, data)
    if not filtered_products:
        await message.answer("По вашему запросу нет товаров.", reply_markup=keyboard)
        return

    for product in filtered_products:
        if product.section.lower() == 'другие':  # Check for lowercase 'другие'
            size_info = ""  # Если раздел "Другие", размер не выводится
        else:
            size_info = f"<b>📏 Размер:</b> {product.size}\n"
        description_text = (
            f"<b>🆔 ID:</b> {product.id}\n"
            f"<b>🏷 Название:</b> {product.name}\n"
            f"<b>📝 Описание:</b> {product.description}\n"
            f"<b>🔍 Раздел:</b> {product.section}\n"
            f"<b>📦 Категория:</b> {product.category}\n"
            f"<b>👤 Тип:</b> {product.gender}\n"
            f"{size_info}"  # Вставляем информацию о размере
            f"<b>💰 Цена:</b> {product.price}\n"
        )
        photos = [
            product.image1,
            product.image2,
            product.image3,
            product.image4,
        ]
        media = [
            types.InputMediaPhoto(media=photo_id, caption=description_text)
            for photo_id in photos
        ]

        # Send the media group with captions
        await message.answer_media_group(
            media=media,
        )
        await callback_query.message.answer(
            text=description_text,
            reply_markup=get_callback_btns(
                btns={
                    "Удалить": f"delete_{product.id}",
                    "Изменить": f"change_{product.id}",
                }
            ),
        )

        await state.clear()
    await message.answer("ОК, вот список товаров ⏫")

