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
            'футболки': 'Футболки',
            'лонгсливы': 'Лонгсливы',
            'худи': 'Худи',
            'свитшоты': 'Свитшоты',
            'толстовки': 'Толстовки',
            'куртки': 'Куртки',
            'жилетки': 'Жилетки',
            'штаны': 'Штаны',
            'шорты': 'Шорты',
            'кепки': 'Кепки'
        },
        'footwear': {
            'ботинки': 'Ботинки',
            'кроссовки': 'Кроссовки',
            'слипоны': 'Слипоны',
            'кеды': 'Кеды',
            'шлепки': 'Шлепки',
            'сандалии': 'Сандалии',
        },
        'others': {
            'сумка': 'Сумка',
            'рюкзак': 'Рюкзак',
            'баф': 'Баф'
        }
    },
    'en': {
        'clothing': {
            'футболки': 'T-shirts',
            'лонгсливы': 'Long sleeves',
            'худи': 'Hoodies',
            'свитшоты': 'Sweatshirts',
            'толстовки': 'Hoodies',
            'куртки': 'Jackets',
            'жилетки': 'Vests',
            'штаны': 'Pants',
            'шорты': 'Shorts',
            'кепки': 'Caps'
        },
        'footwear': {
            'ботинки': 'Boots',
            'кроссовки': 'Sneakers',
            'слипоны': 'Slip-ons',
            'кеды': 'Sneakers',
            'шлепки': 'Flip-flops',
            'сандалии': 'Sandals',
        },
        'others': {
            'сумка': 'Bag',
            'рюкзак': 'Backpack',
            'баф': 'Buff'
    }}

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
        'footwear': ["35", "36", "37", "38", "39", "40",
                     "41", "43", "44", "45",  "46", "47"]
    },
    'en': {
        'clothing': ["XS", "S", "M", "L", "XL", "XXL"],
        'footwear': ["35", "36", "37", "38", "39", "40",
                     "41", "43", "44", "45",  "46", "47"]
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
