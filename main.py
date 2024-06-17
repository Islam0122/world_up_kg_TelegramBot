import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

from handlers.group_panel.user_group_private import user_group_router
from middlewares.db import DataBaseSession

load_dotenv(find_dotenv())

from database.engine import create_db, drop_db, session_maker
# ->>>>>>>>>>> admin_panel
from handlers.admin_panel.send_mesage import send_message_private_router
from handlers.admin_panel.start_admin import admin_private_router
from handlers.admin_panel.change_product import add_product_router
from handlers.admin_panel.catalog_admin import catalog_admin_router
from handlers.admin_panel.admin_search import admin_search_products_router

# ->>>>>>  user_panel
from handlers.user_panel.catalog import catalog_router
from handlers.user_panel.order_functions import order_router
from handlers.user_panel.search_functions import search_products_router
from handlers.user_panel.popular_products import popular_products_router
from handlers.user_panel.review_functions import review_private_router
from handlers.user_panel.about_us import about_private_router
from handlers.user_panel.help_functions import help_private_router
from handlers.user_panel.unknown_functions import unknown_private_router
from handlers.user_panel.start_functions import user_private_router

from common.bot_cmds_list import private

# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query',]

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bot.my_admins_list = [5627082052, 974193106, ]

dp = Dispatcher()

dp.include_router(add_product_router)
dp.include_router(catalog_router)
dp.include_router(send_message_private_router)
dp.include_router(order_router)
dp.include_router(admin_search_products_router)
dp.include_router(search_products_router)
dp.include_router(popular_products_router)
dp.include_router(catalog_admin_router)
dp.include_router(admin_private_router)
dp.include_router(review_private_router)
dp.include_router(about_private_router)
dp.include_router(user_private_router)
dp.include_router(help_private_router)
dp.include_router(unknown_private_router)
dp.include_router(user_group_router)

async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()
    await bot.send_message(bot.my_admins_list[0], "Сервер успешно запущен! 😊 Привет, босс!")


async def on_shutdown(bot):
    await bot.send_message(bot.my_admins_list[0], "Сервер остановлен. 😔 Проверьте его состояние, босс!")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
