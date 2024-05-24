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
