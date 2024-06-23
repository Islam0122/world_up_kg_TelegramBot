from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_panel.keyboards import get_sections_keyboard, get_categories_keyboard, get_genders_keyboard, \
    get_sizes_keyboard
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

catalog_router = Router()
catalog_router.message.filter(ChatTypeFilter(["private"]))


class CatalogFilters(StatesGroup):
    SECTION = State()
    CATEGORY = State()
    SIZE = State()
    GENDER = State()



@catalog_router.message(Command("catalog"))
async def start_catalog_filtering(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption=texts[language]['choose_section'],
        parse_mode="HTML",
        reply_markup=get_sections_keyboard(language)
    )
    await state.set_state(CatalogFilters.SECTION)


@catalog_router.callback_query(F.data.startswith("catalog"))
async def start_catalog_filtering(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await callback_query.message.answer_photo(
        photo=types.FSInputFile('media/images/scale_1200.png'),
        caption=texts[language]['choose_section'],
        parse_mode="HTML",
        reply_markup=get_sections_keyboard(language)
    )
    await state.set_state(CatalogFilters.SECTION)




@catalog_router.callback_query(CatalogFilters.SECTION, F.data.startswith("section_"))
async def process_section_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_section = callback_query.data.split('_')[1]

    await state.update_data(section=selected_section)
    await state.set_state(CatalogFilters.CATEGORY)
    data = await state.get_data()
    await callback_query.message.answer(texts[language]['choose_category'],
                                        reply_markup=get_categories_keyboard(data['section'],language))


@catalog_router.callback_query(CatalogFilters.CATEGORY, F.data.startswith("category_"))
async def process_category_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_category = callback_query.data.split('_')[1]
    await state.update_data(category=selected_category)
    await state.set_state(CatalogFilters.CATEGORY)
    data = await state.get_data()
    if data['section'] in ['другие', 'Другие']:
        await state.set_state(CatalogFilters.GENDER)
        await callback_query.message.answer(texts[language]['choose_gender'], reply_markup=get_genders_keyboard(language))
    else:
        await state.set_state(CatalogFilters.SIZE)
        await callback_query.message.answer(texts[language]['choose_size'], reply_markup=get_sizes_keyboard(data['section'],language))


@catalog_router.callback_query(CatalogFilters.SIZE, F.data.startswith("size_"))
async def process_size_choice(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_size = callback_query.data.split('_')[1]
    await state.update_data(size=selected_size)
    await state.set_state(CatalogFilters.GENDER)
    await callback_query.message.answer(texts[language]['choose_gender'], reply_markup=get_genders_keyboard(language))


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
    await callback_query.answer()
    user_id = callback_query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    selected_gender = callback_query.data.split('_')[1]
    await state.update_data(gender=selected_gender)

    try:
        products = await orm_get_products(session)
    except Exception as e:
        await callback_query.message.answer(f"An error occurred while fetching products: {e}")
        return

    data = await state.get_data()
    filtered_products = filter_products(products, data)

    if not filtered_products:
        await callback_query.message.answer(texts[language]['no_products_found'], reply_markup=ReplyKeyboardRemove())
        return

    for product in filtered_products:
        product_name = product.name if language == 'ru' else translator.translate(product.name, src='ru',
                                                                                  dest='en').text
        product_description = product.description if language == 'ru' else translator.translate(product.description,
                                                                                                src='ru',
                                                                                                dest='en').text
        section = product.section if language == 'ru' else translator.translate(product.section, src='ru',
                                                                                dest='en').text
        category = product.category if language == 'ru' else translator.translate(product.category, src='ru',
                                                                                  dest='en').text
        gender = product.gender if language == 'ru' else translator.translate(product.gender, src='ru', dest='en').text
        price = product.price if language == 'ru' else translator.translate(product.price, src='ru',
                                                                                  dest='en').text


        description_text = texts[language]['product_details'].format(
            id=product.id,
            name=product_name,
            description=product_description,
            section=section,
            category=category,
            gender=gender,
            size_info=f"<b>Size:</b> {product.size}\n" if product.section.lower() != 'others' or 'другие' else "",
            # Adjust based on the section
            price=price,
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
        await callback_query.message.answer_media_group(
            media=media,
        )
        await callback_query.message.answer(description_text )

    await state.clear()
