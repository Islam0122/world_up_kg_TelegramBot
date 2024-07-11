from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

button_texts = {
    'ru': {
        'clothing': 'Одежда',
        'footwear': 'Обувь',
        'others': 'Другие'
    },
    'en': {
        'clothing': 'Clothing',
        'footwear': 'Footwear',
        'others': 'Others'
    }
}


# Function to generate the keyboard based on the user's language preference
def get_sections_keyboard(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=button_texts[language]['clothing'], callback_data="section_Одежда"),
        InlineKeyboardButton(text=button_texts[language]['footwear'], callback_data="section_Обувь"),
        InlineKeyboardButton(text=button_texts[language]['others'], callback_data="section_Другие"),
    )
    return keyboard.adjust(3, ).as_markup()


category_texts = {
    'ru': {
        'clothing': {
            'футболка': 'Футболка',
            'штаны': 'Штаны',
            'куртки': 'Куртки',
            'худи': 'Худи',
            'лонгсливы': 'Лонгсливы',
            'кофты': 'Кофты',
            'шорты': 'Шорты'
        },
        'footwear': {
            'кроссовки': 'Кроссовки',
            'ботинки': 'Ботинки',
            'сандалии': 'Сандалии',
            'туфли': 'Туфли',
            'сапоги': 'Сапоги',
            'классические ботинки':'Классические ботинки'
        },
        'others': {
            'электроника': 'Электроника',
            'книги': 'Книги',
            'аксессуары': 'Аксессуары',
            'игрушки': 'Игрушки',
            'спорттовары': 'Спорттовары'
        }
    },
    'en': {
        'clothing': {
            'футболка': 'T-shirts',
            'штаны': 'Pants',
            'куртки': 'Jackets',
            'худи': 'Hoodies',
            'лонгсливы': 'Long sleeves',
            'кофты': 'Sweaters',
            'шорты': 'Shorts'
        },
        'footwear': {
            'кроссовки': 'Sneakers',
            'ботинки': 'Boots',
            'сандалии': 'Sandals',
            'туфли': 'Shoes',
            'сапоги': 'High Boots',
            'классические ботинки':'classic boots'
        },
        'others': {
            'электроника': 'Electronics',
            'книги': 'Books',
            'аксессуары': 'Accessories',
            'игрушка': 'Toys',
            'спорттовары': 'Sport goods'
        }
    }

}


# Function to generate the keyboard based on the user's language preference and section
def get_categories_keyboard(section, language):
    keyboard = InlineKeyboardBuilder()

    if section.lower() == "одежда":
        for key, value in category_texts[language]['clothing'].items():
            keyboard.add(InlineKeyboardButton(text=value, callback_data=f"category_{key}"))

    elif section.lower() == "обувь":
        for key, value in category_texts[language]['footwear'].items():
            keyboard.add(InlineKeyboardButton(text=value, callback_data=f"category_{key}"))
    else:
        for key, value in category_texts[language]['others'].items():
            keyboard.add(InlineKeyboardButton(text=value, callback_data=f"category_{key}"))

    keyboard.add(InlineKeyboardButton(text="↩️", callback_data="back_section"))

    return keyboard.adjust(3).as_markup()  # Adjust buttons to display in a suitable layout


size_texts = {
    'ru': {
        'clothing': ["XS", "S", "M", "L", "XL", "XXL"],
        'footwear': ["35", "36", "37", "37,5-38", "38,5-39", "39", "39,5-40", "40", "40-40,5", "40,5-41",
                     "41,5-42", "42", "42,5-43", "43", "43-44", "44-45", "45", "45-46", "46", "46-47"]
    },
    'en': {
        'clothing': ["XS", "S", "M", "L", "XL", "XXL"],
        'footwear': ["35", "36", "37", "37.5-38", "38.5-39", "39", "39.5-40", "40", "40-40.5", "40.5-41",
                     "41.5-42", "42", "42.5-43", "43", "43-44", "44-45", "45", "45-46", "46", "46-47"]
    }
}

gender_texts = {
    'ru': {
        'male': "Мужской",
        'female': "Женская",
        'unisex': "Для всех"
    },
    'en': {
        'male': "Male",
        'female': "Female",
        'unisex': "For all"
    }
}

def get_sizes_keyboard(section, language):
    keyboard = InlineKeyboardBuilder()

    if section.lower() == "одежда":
        sizes = size_texts[language]['clothing']
    else:
        sizes = size_texts[language]['footwear']

    for size in sizes:
        keyboard.add(InlineKeyboardButton(text=size, callback_data=f"size_{size}"))

    keyboard.add(InlineKeyboardButton(text="↩️", callback_data="back_category"))
    return keyboard.adjust(5).as_markup()  # Adjust buttons to display in a suitable layout

# Function to generate genders keyboard based on the user's language preference

def get_genders_keyboard(language):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text=gender_texts[language]['male'], callback_data="gender_Мужской"),
        InlineKeyboardButton(text=gender_texts[language]['female'], callback_data="gender_Женская"),
        InlineKeyboardButton(text=gender_texts[language]['unisex'], callback_data="gender_Для всех")
    )
    keyboard.add(InlineKeyboardButton(text="↩️", callback_data="back_size"))
    return keyboard.adjust(3).as_markup()
