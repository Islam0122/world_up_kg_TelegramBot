from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_panel.keyboards import *
from handlers.user_panel.search_functions import translator
from handlers.user_panel.start_functions import user_preferences
from keyboard_list.reply import get_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from database.model import Product
from database.orm_query import orm_add_product, orm_delete_product, orm_get_product, orm_update_product

from database.orm_query import orm_get_products
from keyboard_list.inline import get_callback_btns

texts = {
    'ru': {
        'choose_section': "Выберите раздел, в котором вы ищете товар:",
        'choose_category': "Выберите категорию товара:",
        'choose_size': "Выберите размер товара:",
        'choose_gender': "Выберите пол товара:",
        'no_products_found': "По вашему запросу нет товаров.",
        'product_details': (
            "<b>🆔 ID:</b> {id}\n"
            "<b>🏷 Название:</b> {name}\n"
            "<b>📝 Описание:</b> {description}\n"
            "<b>🔍 Раздел:</b> {section}\n"
            "<b>📦 Категория:</b> {category}\n"
            "<b>👤 Тип:</b> {gender}\n"
            "{size_info}"
            "<b>💰 Цена:</b> {price}\n"
        ),
    },
    'en': {
        'choose_section': "Choose the section in which you are looking for a product:",
        'choose_category': "Choose the product category:",
        'choose_size': "Choose the product size:",
        'choose_gender': "Choose the product gender:",
        'no_products_found': "No products found for your request.",
        'product_details': (
            "<b>🆔 ID:</b> {id}\n"
            "<b>🏷 Name:</b> {name}\n"
            "<b>📝 Description:</b> {description}\n"
            "<b>🔍 Section:</b> {section}\n"
            "<b>📦 Category:</b> {category}\n"
            "<b>👤 Gender:</b> {gender}\n"
            "{size_info}"
            "<b>💰 Price:</b> {price}\n"
        ),
    }
}



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
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption="Выберите раздел, в котором вы ищете товар:",
        parse_mode="HTML",
        reply_markup=get_sections_keyboard(language)
    )

    await state.set_state(AdminCatalogFilters.SECTION)


@catalog_admin_router.callback_query((F.data.startswith("admin_catalog")))
async def start_catalog_filtering(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await callback_query.message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption=texts[language]['choose_section'],
        parse_mode="HTML",
        reply_markup=get_sections_keyboard(language)
    )
    await state.set_state(AdminCatalogFilters.SECTION)


@catalog_admin_router.callback_query(AdminCatalogFilters.SECTION, F.data.startswith("section_"))
async def process_section_choice(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_section = callback_query.data.split('_')[1]

    await state.update_data(section=selected_section)
    await state.set_state(AdminCatalogFilters.CATEGORY)
    data = await state.get_data()
    await callback_query.message.edit_caption(
        caption=texts[language]['choose_category'],
        reply_markup=get_categories_keyboard(data['section'], language)
    )

@catalog_admin_router.callback_query(AdminCatalogFilters.CATEGORY, F.data.startswith("category_"))
async def process_category_choice(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_category = callback_query.data.split('_')[1]
    await state.update_data(category=selected_category)
    data = await state.get_data()
    if data['section'] in ['другие', 'Другие']:
        await state.set_state(AdminCatalogFilters.GENDER)
        await callback_query.message.edit_caption(caption=texts[language]['choose_gender'],
                                            reply_markup=get_genders_keyboard(language))
    else:
        await state.set_state(AdminCatalogFilters.SIZE)
        await callback_query.message.edit_caption(caption=texts[language]['choose_size'],
                                            reply_markup=get_sizes_keyboard(data['section'], language))


@catalog_admin_router.callback_query(AdminCatalogFilters.SIZE, F.data.startswith("size_"))
async def process_size_choice(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_size = callback_query.data.split('_')[1]
    await state.update_data(size=selected_size)
    await state.set_state(AdminCatalogFilters.GENDER)
    await callback_query.message.edit_caption(
        caption=texts[language]['choose_gender'],
        reply_markup=get_genders_keyboard(language)
    )


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

@catalog_admin_router.callback_query(F.data == "back_section")
async def back_to_sections(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await state.set_state(AdminCatalogFilters.SECTION)
    await callback_query.message.edit_caption(
        caption=texts[language]['choose_section'],
        reply_markup=get_sections_keyboard(language)
    )


@catalog_admin_router.callback_query(F.data == "back_category")
async def back_to_categories(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    data = await state.get_data()
    await state.set_state(AdminCatalogFilters.CATEGORY)
    await callback_query.message.edit_caption(
        caption=texts[language]['choose_category'],
        reply_markup=get_categories_keyboard(data['section'], language)
    )


@catalog_admin_router.callback_query(F.data == "back_size")
async def back_to_sizes(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    data = await state.get_data()
    selected_section = data.get('section', '').lower()

    if selected_section in ['другие', 'others']:
        await state.set_state(AdminCatalogFilters.CATEGORY)
        await callback_query.message.edit_caption(
            caption=texts[language]['choose_category'],
            reply_markup=get_categories_keyboard(selected_section, language)
        )
    else:
        await state.set_state(AdminCatalogFilters.SIZE)
        await callback_query.message.edit_caption(
            caption=texts[language]['choose_size'],
            reply_markup=get_sizes_keyboard(selected_section, language)
        )