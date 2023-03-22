# - *- coding: utf- 8 - *-
import os
import sys

import colorama
from aiogram import executor, Dispatcher

from tgbot.data.config import get_admins
from tgbot.data.loader import scheduler
from tgbot.handlers import dp
from tgbot.middlewares import setup_middlewares
from tgbot.services.api_session import AsyncSession
from tgbot.services.api_sqlite import create_dbx
from tgbot.utils.misc.bot_commands import set_commands
from tgbot.utils.misc.bot_filters import IsPrivate
from tgbot.utils.misc.bot_logging import bot_logger
from tgbot.utils.misc_functions import (check_update, check_bot_data, startup_notify, update_profit_day,
                                        update_profit_week, autobackup_admin, check_mail)

colorama.init()


# Запуск шедулеров
async def scheduler_start(rSession):
    scheduler.add_job(update_profit_day, trigger="cron", hour=00)
    scheduler.add_job(update_profit_week, trigger="cron", day_of_week="mon", hour=00, minute=1)
    scheduler.add_job(autobackup_admin, trigger="cron", hour=00)
    scheduler.add_job(check_update, trigger="cron", hour=00, args=(rSession,))
    scheduler.add_job(check_mail, trigger="cron", hour=12, args=(rSession,))


# Выполнение функции после запуска бота
async def on_startup(dp: Dispatcher):
    rSession = AsyncSession()
    dp.bot['rSession'] = rSession

    await dp.bot.delete_webhook()
    await dp.bot.get_updates(offset=-1)

    await set_commands(dp)
    await check_bot_data()
    await scheduler_start(rSession)
    await startup_notify(dp, rSession)

    bot_logger.warning("BOT WAS STARTED")
    print(colorama.Fore.LIGHTYELLOW_EX + f"~~~~~ Bot was started - @{(await dp.bot.get_me()).username} ~~~~~")
    print(colorama.Fore.LIGHTBLUE_EX + "~~~~~ TG developer - @djimbox ~~~~~")
    print(colorama.Fore.RESET)

    if len(get_admins()) == 0: print("***** ENTER ADMIN ID IN settings.ini *****")


# Выполнение функции после выключения бота
async def on_shutdown(dp: Dispatcher):
    rSession: AsyncSession = dp.bot['rSession']
    await rSession.close()

    await dp.storage.close()
    await dp.storage.wait_closed()
    await (await dp.bot.get_session()).close()

    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    create_dbx()

    scheduler.start()
    dp.filters_factory.bind(IsPrivate)  # Подключение фильтра приватности
    setup_middlewares(dp)  # Подключение миддлварей

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
