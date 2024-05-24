from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Меню 📋")],
        [KeyboardButton(text="О нас ℹ️")],
        [
            KeyboardButton(text="Варианты доставки 🚚"),
            KeyboardButton(text="Варианты оплаты 💳"),
            KeyboardButton(text="Оставить отзыв ✍️")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что Вас интересует?'
)
del_start_keyboard = ReplyKeyboardRemove()

# start_kb2 = ReplyKeyboardBuilder()
# start_kb2.add(
#     KeyboardButton(text="Меню"),
#     KeyboardButton(text="О магазине"),
#     KeyboardButton(text="Варианты доставки"),
#     KeyboardButton(text="Варианты оплаты"),
# )
# start_kb2.adjust(2, 2)

test_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать опрос", request_poll=KeyboardButtonPollType()),
        ],
        [
            KeyboardButton(text="Отправить номер ☎️", request_contact=True),
            KeyboardButton(text="Отправить локацию 🗺️", request_location=True),
        ],
    ],
    resize_keyboard=True,
)

def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
):

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)
