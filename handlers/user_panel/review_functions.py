from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from database.config import chat_id
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_panel.start_functions import user_preferences

cancel_button_texts = {
    'ru': "Отмена",
    'en': "Cancel",
}
# Reply keyboard for cancel action
def key(language):
 keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=cancel_button_texts[language])],
    ],
    resize_keyboard=True,
 )
 return keyboard

# English and Russian versions of review prompts
review_prompts = {
    'ru': {
        'start': "Мы были бы рады услышать ваш отзыв о нашем сервисе. 😊\nПожалуйста, напишите, что вы думаете о нас. 💬",
        'success': "Ваш отзыв был успешно отправлен! Спасибо вам за поддержку и обратную связь! 🌟\n\n"
                   "Вы также можете присоединиться к нашему чату для обсуждения идей и предложений: "
                   "<a href='https://t.me/WourldUpKg'>Наш чат</a>"
    },
    'en': {
        'start': "We would love to hear your feedback about our service. 😊\nPlease write what you think about us. 💬",
        'success': "Your review has been successfully submitted! Thank you for your support and feedback! 🌟\n\n"
                   "You can also join our chat for discussion of ideas and suggestions: "
                   "<a href='https://t.me/WourldUpKg'>Our Chat</a>"
    }
}


# State group for review process
class ReviewState(StatesGroup):
    WaitingForReview = State()


# Router for handling review messages
review_private_router = Router()
review_private_router.message.filter(ChatTypeFilter(['private']))

cancel_messages = {
    'ru': "🚫 Действие отменено",
    'en': "🚫 Action cancelled",
}


# Handler for starting the review process
@review_private_router.message((F.text.lower().contains('✍️ Оставить отзыв')) |
                               (F.text.lower() == 'review'))
@review_private_router.message(Command("review"))
async def send_review_request(message: types.Message, state: FSMContext):
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')  # Replace with your language logic
    await message.answer(
        review_prompts[language]['start'], reply_markup=key(language)
    )
    await state.set_state(ReviewState.WaitingForReview)


# Callback query handler (if needed for triggering review process)
@review_private_router.callback_query((F.data.startswith("review")))
async def send_review_request_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru') # Replace with your language logic
    await query.message.answer(
        review_prompts[language]['start'], reply_markup=key(language)
    )
    await state.set_state(ReviewState.WaitingForReview)


# Handler for processing the review message
@review_private_router.message(ReviewState.WaitingForReview)
async def process_review(message: types.Message, state: FSMContext, bot: Bot):
    keyboard = ReplyKeyboardRemove()
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')  # Replace with your language logic
    if message.text:
        user_info = f"{message.from_user.first_name}"
        if message.from_user.last_name:
            user_info += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"

        # Send the review to the designated chat or admin
        if language == 'ru':
            await bot.send_message(
                chat_id,
                f"📝 Новый отзыв от {user_info}:\n\n{message.text}\n\n"
                "Спасибо вам за вашу поддержку и обратную связь! 🙏",
            )
        if language == 'en':
            await bot.send_message(
                chat_id,
                f"📝 New review from {user_info}:\n\n{message.text}\n\n"
                "Thank you for your support and feedback! 🙏",
            )
        # Notify the user that their review was successfully sent
        await message.answer(
            review_prompts[language]['success'], reply_markup=keyboard, parse_mode='HTML'
        )
        await state.clear()  # Clear the state after processing

    else:
        if language == 'ru':
            await message.answer("Пожалуйста, напишите что-нибудь, чтобы мы знали, что вы думаете. 😊",reply_markup=key(language))
        if language == 'en':
            await message.answer(
                "Please write something so we know what you think. 😊", reply_markup=key(language)
            )
