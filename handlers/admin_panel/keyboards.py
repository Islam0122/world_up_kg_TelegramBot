from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="start_admin"),
    )
    return keyboard.adjust().as_markup()
# Функция для получения клавиатуры с разделами товаров
def get_sections_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [ KeyboardButton(text="Одежда"),KeyboardButton(text="Обувь"),KeyboardButton(text="Другие")],
            [KeyboardButton(text="Отмена"),KeyboardButton(text="Назад")],

        ],
        resize_keyboard=True,

    )
    return keyboard

def get_categories_clothing_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="футболки"), KeyboardButton(text="лонгсливы"),  # Long sleeves
            ],
            [KeyboardButton(text="куртки"), KeyboardButton(text="жилетки"),  # Jackets
             ],
            [ KeyboardButton(text="cвитшоты"), KeyboardButton(text="толстовки")],
            [KeyboardButton(text="шорты"), KeyboardButton(text="штаны"),],
            [
                KeyboardButton(text="кепки"),
                KeyboardButton(text="худи"),

            ],
            [
                KeyboardButton(text="Отмена"),
                KeyboardButton(text="Назад")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_categories_footwear_keyboard():  # -> обувь
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="кроссовки"), KeyboardButton(text="ботинки"), KeyboardButton(text="сандалии")],
            [ KeyboardButton(text="слипоны"), KeyboardButton(text="кеды")],
            [KeyboardButton(text="шлепки"),KeyboardButton(text="Отмена"), KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_categories_wear_keyboard():  # -> о другие
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="сумка"), KeyboardButton(text="рюкзак"),
            ],
            [
                KeyboardButton(text="баф"),
            ],
            [
                KeyboardButton(text="Отмена"), KeyboardButton(text="Назад")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_gender_gen_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [ KeyboardButton(text="Мужской"),
              KeyboardButton(text="Женская"),
              KeyboardButton(text="Для всех")],
            [
                KeyboardButton(text="Отмена"),
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_gender_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [ KeyboardButton(text="Мужской"),
              KeyboardButton(text="Женская"),
              KeyboardButton(text="Для всех")],
            [
                KeyboardButton(text="Отмена"), KeyboardButton(text="Назад")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


# Функция для получения клавиатуры с размерами для одежды
def get_sizes_clothing_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="XS"), KeyboardButton(text="S"), KeyboardButton(text="M")],
            [KeyboardButton(text="L"), KeyboardButton(text="XL"), KeyboardButton(text="XXL")],
            [KeyboardButton(text="Отмена"), KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_sizes_footwear_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="35"), KeyboardButton(text="36"), KeyboardButton(text="37"),
             KeyboardButton(text="38"), KeyboardButton(text="39")],
            [KeyboardButton(text="40"), KeyboardButton(text="41"), KeyboardButton(text="42"),
             KeyboardButton(text="43"), KeyboardButton(text="44"), KeyboardButton(text="45")],
            [KeyboardButton(text="46"), KeyboardButton(text="47")],
            [KeyboardButton(text="Отмена"), KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard
