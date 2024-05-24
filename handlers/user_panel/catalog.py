from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_panel.keyboards import get_sections_keyboard, get_categories_keyboard, get_genders_keyboard, \
    get_sizes_keyboard
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product

from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

catalog_router = Router()
catalog_router.message.filter(ChatTypeFilter(["private"]))


class CatalogFilters(StatesGroup):
    SECTION = State()
    CATEGORY = State()
    SIZE = State()
    GENDER = State()



@catalog_router.message(Command("catalog"))
async def start_catalog_filtering(message: types.Message, state: FSMContext):
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption="Выберите раздел, в котором вы ищете товар:",
        parse_mode="HTML",
        reply_markup=get_sections_keyboard()
    )

    await state.set_state(CatalogFilters.SECTION)


@catalog_router.callback_query(F.data.startswith("catalog"))
async def start_catalog_filtering(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption="Выберите раздел, в котором вы ищете товар:",
        parse_mode="HTML",
        reply_markup=get_sections_keyboard()
    )

    await state.set_state(CatalogFilters.SECTION)


@catalog_router.callback_query(CatalogFilters.SECTION, F.data.startswith("section_"))
async def process_section_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()

    selected_section = callback_query.data.split('_')[1]

    await state.update_data(section=selected_section)
    await state.set_state(CatalogFilters.CATEGORY)
    data = await state.get_data()
    await callback_query.message.answer("Выберите категорию товара:",
                                        reply_markup=get_categories_keyboard(data['section']))


@catalog_router.callback_query(CatalogFilters.CATEGORY, F.data.startswith("category_"))
async def process_category_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    selected_category = callback_query.data.split('_')[1]
    await state.update_data(category=selected_category)
    await state.set_state(CatalogFilters.CATEGORY)
    data = await state.get_data()
    if data['section'] == 'другие' or data['section'] == 'Другие':
        await state.set_state(CatalogFilters.GENDER)
        await callback_query.message.answer("Выберите тип товара:", reply_markup=get_genders_keyboard())
    else:
        await state.set_state(CatalogFilters.SIZE)
        await callback_query.message.answer("Выберите размер товара:", reply_markup=get_sizes_keyboard(data['section']))


@catalog_router.callback_query(CatalogFilters.SIZE, F.data.startswith("size_"))
async def process_size_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    selected_size = callback_query.data.split('_')[1]
    await state.update_data(size=selected_size)
    await state.set_state(CatalogFilters.GENDER)
    await callback_query.message.answer("Выберите пол товара:", reply_markup=get_genders_keyboard())

def filter_products(products, filters):
    filtered_products = []
    for product in products:
        if (filters.get('size', 'any') == 'any' or product.size.lower() == filters['size'].lower()) and \
                (filters.get('section', 'any') == 'any' or product.section.lower() == filters['section'].lower()) and \
                (filters.get('category', 'any') == 'any' or product.category.lower() == filters['category'].lower()) and \
                (filters.get('gender', 'any') == 'any' or product.gender.lower() == filters['gender'].lower()):
            filtered_products.append(product)
    return filtered_products
@catalog_router.callback_query(CatalogFilters.GENDER, F.data.startswith("gender_"))
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

        await message.answer_photo(
            product.image,
            caption=description_text,
            reply_markup=get_callback_btns(
                btns={
                    "Купить": f"buy_{product.id}",
                },
            ),  # Add reply_markup parameter here to remove the keyboard
        )

        await state.clear()
