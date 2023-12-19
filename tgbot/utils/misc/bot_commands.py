# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from tgbot.data.config import get_admins

# Команды для юзеров
user_commands = [
    BotCommand(command='start', description='♻️ Перезапустить бота'),
    BotCommand(command='support', description='☎️ Поддержка'),
    BotCommand(command='faq', description='❔ FAQ'),
]

# Команды для админов
admin_commands = [
    BotCommand(command='start', description='♻️ Перезапустить бота'),
    BotCommand(command='support', description='☎️ Поддержка'),
    BotCommand(command='faq', description='❔ FAQ'),
    BotCommand(command='db', description='📦 Получить Базу Данных'),
    BotCommand(command='log', description='🖨 Получить логи'),
]


# Установка команд
async def set_commands(bot: Bot):
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    for admin in get_admins():
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin))
        except:
            ...
