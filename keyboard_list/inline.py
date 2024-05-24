from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Определение функции с именем get_callback_btns
def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    # Создание объекта клавиатуры типа InlineKeyboardBuilder
    keyboard = InlineKeyboardBuilder()

    # Итерация по элементам словаря btns
    for text, data in btns.items():
        # Добавление кнопки в клавиатуру с текстом и данными колбэка
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    # Настройка размеров кнопок и возврат разметки клавиатуры в виде разметки
    return keyboard.adjust(*sizes).as_markup()


# Определение функции с именем get_url_btns
def get_url_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    # Создание объекта клавиатуры типа InlineKeyboardBuilder
    keyboard = InlineKeyboardBuilder()

    # Итерация по элементам словаря btns
    for text, url in btns.items():
        # Добавление кнопки в клавиатуру с текстом и URL
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    # Настройка размеров кнопок и возврат разметки клавиатуры в виде разметки
    return keyboard.adjust(*sizes).as_markup()



# Определение функции с именем get_inlineMix_btns
def get_inlineMix_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    # Создание объекта клавиатуры типа InlineKeyboardBuilder
    keyboard = InlineKeyboardBuilder()

    # Итерация по элементам словаря btns
    for text, value in btns.items():
        # Проверка, содержит ли значение URL-адрес
        if '://' in value:
            # Если значение содержит URL, добавляем кнопку с URL
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            # Если значение не содержит URL, добавляем Callback-кнопку
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    # Настройка размеров кнопок и возврат разметки клавиатуры в виде разметки
    return keyboard.adjust(*sizes).as_markup()