# - *- coding: utf- 8 - *-
import asyncio
import os
import sys

import colorama
from aiogram import Dispatcher, Bot

from tgbot.data.config import get_admins, BOT_TOKEN, BOT_SCHEDULER
from tgbot.database.db_helper import create_dbx
from tgbot.middlewares import register_all_middlwares
from tgbot.routers import register_all_routers
from tgbot.services.api_session import AsyncRequestSession
from tgbot.utils.misc.bot_commands import set_commands
from tgbot.utils.misc.bot_logging import bot_logger
from tgbot.utils.misc.bot_models import ARS
from tgbot.utils.misc_functions import (check_update, check_bot_username, startup_notify, update_profit_day,
                                        update_profit_week, autobackup_admin, check_mail, update_profit_month,
                                        autosettings_unix)

colorama.init()


# Запуск шедулеров
async def scheduler_start(bot: Bot, arSession: ARS):
    BOT_SCHEDULER.add_job(update_profit_month, trigger="cron", day=1, hour=00, minute=00, second=5)
    BOT_SCHEDULER.add_job(update_profit_week, trigger="cron", day_of_week="mon", hour=00, minute=00, second=10)
    BOT_SCHEDULER.add_job(update_profit_day, trigger="cron", hour=00, minute=00, second=15, args=(bot,))
    BOT_SCHEDULER.add_job(autobackup_admin, trigger="cron", hour=00, args=(bot,))
    BOT_SCHEDULER.add_job(check_update, trigger="cron", hour=00, args=(bot, arSession,))
    BOT_SCHEDULER.add_job(check_mail, trigger="cron", hour=12, args=(bot, arSession,))


# Запуск бота и базовых функций
async def main():
    BOT_SCHEDULER.start()  # Запуск Шедулера
    dp = Dispatcher()  # Образ Диспетчера
    arSession = AsyncRequestSession()  # Пул асинхронной сессии запросов
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")  # Образ Бота

    register_all_middlwares(dp)  # Регистрация всех мидлварей
    register_all_routers(dp)  # Регистрация всех роутеров

    try:
        await autosettings_unix()  # Автонастройка UNIX времени в БД
        await set_commands(bot)  # Установка команд
        await check_bot_username(bot)  # Проверка юзернейма бота в БД
        await check_update(bot, arSession)  # Проверка обновлений
        await check_mail(bot, arSession)  # Оповещение обновлений
        await startup_notify(bot, arSession)  # Рассылка при запуске бота
        await scheduler_start(bot, arSession)  # Подключение шедулеров

        bot_logger.warning("BOT WAS STARTED")
        print(colorama.Fore.LIGHTYELLOW_EX + f"~~~~~ Bot was started - @{(await bot.get_me()).username} ~~~~~")
        print(colorama.Fore.LIGHTBLUE_EX + "~~~~~ TG developer - @djimbox ~~~~~")
        print(colorama.Fore.RESET)

        if len(get_admins()) == 0: print("***** ENTER ADMIN ID IN settings.ini *****")

        await bot.delete_webhook()
        await bot.get_updates(offset=-1)

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            arSession=arSession,
        )
    finally:
        await arSession.close()
        await bot.session.close()


if __name__ == "__main__":
    create_dbx()  # Генерация БД и таблиц

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        bot_logger.warning("Bot was stopped")
    finally:
        if sys.platform.startswith("win"):
            os.system("cls")
        else:
            os.system("clear")
