from string import punctuation
from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart, Command, or_f
from filter.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))
user_group_router.edited_message.filter(ChatTypeFilter(['group', 'supergroup']))

restricted_words = {'кабан', 'хомяк', 'выхухоль'}


@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message):
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f"{message.from_user.first_name}, соблюддайте порядок в чате!")
        await message.delete()
