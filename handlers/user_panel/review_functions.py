from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database.config import chat_id
from filter.chat_types import ChatTypeFilter, IsAdmin

review_private_router = Router()
review_private_router.message.filter(ChatTypeFilter(['private']))

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
)


class ReviewState(StatesGroup):
    WaitingForReview = State()


@review_private_router.message(StateFilter("*"), Command("отмена"))
@review_private_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("🚫 Действие отменено")


@review_private_router.message((F.text.lower().contains('✍️ Оставить отзыв')) |
                               (F.text.lower() == 'review'))
@review_private_router.message(Command("review"))
async def send_review_request(message: types.Message, state: FSMContext):
    await message.answer(
        "Мы были бы рады услышать ваш отзыв о нашем сервисе. 😊\n"
        "Пожалуйста, напишите, что вы думаете о нас. 💬", reply_markup=keyboard
    )
    await state.set_state(ReviewState.WaitingForReview)


@review_private_router.callback_query((F.data.startswith("review")))
async def send_review_request_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    message = query.message
    await message.answer(
        "Мы были бы рады услышать ваш отзыв о нашем сервисе. 😊\n"
        "Пожалуйста, напишите, что вы думаете о нас. 💬", reply_markup=keyboard
    )
    await state.set_state(ReviewState.WaitingForReview)

@review_private_router.message(ReviewState.WaitingForReview)
async def process_review(message: types.Message, state: FSMContext, bot: Bot):
    keyboard = ReplyKeyboardRemove()
    if message.text:
        user_info = f"{message.from_user.first_name}"
        if message.from_user.last_name:
            user_info += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"

        await bot.send_message(
            chat_id,
            f"📝 Новый отзыв от {user_info}:\n\n{message.text}\n\n"
            "Спасибо вам за вашу поддержку и обратную связь! 🙏",
        )
        await message.answer(
            f"Ваш отзыв был успешно отправлен! Спасибо вам за поддержку и обратную связь! 🌟"
            f"\n\n"
            f"Вы также можете присоединиться к нашему чату для обсуждения идей и предложений:"
            f" <a href='https://t.me/WourldUpKg'>Наш чат</a>", reply_markup=keyboard
        )
        await state.clear()

    else:
        await message.answer(
            "Пожалуйста, напишите хоть что-то, чтобы мы знали, что вы думаете. 😊"
        )
