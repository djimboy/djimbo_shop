# - *- coding: utf- 8 - *-
import asyncio

from aiogram import executor

import filters
import middlewares
from handlers import dp
from utils.db_api.sqlite import create_bdx
from utils.other_func import on_startup_notify, update_last_profit, check_update_bot, update_profit
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    filters.setup(dp)
    middlewares.setup(dp)

    await set_default_commands(dp)
    await on_startup_notify(dp)

    asyncio.create_task(update_last_profit())
    asyncio.create_task(check_update_bot())
    print("~~~~~ Bot was started ~~~~~")


if __name__ == "__main__":
    create_bdx()
    update_profit()

    executor.start_polling(dp, on_startup=on_startup)
