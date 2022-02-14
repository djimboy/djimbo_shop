from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import admins
from utils import get_settingsx
from utils.db_api.sqlite import get_userx


# Проверка на написания сообщения в ЛС бота
class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE


# Проверка на админа
class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        if str(message.from_user.id) in admins:
            return True
        else:
            return False

# Проверка на возможность покупки товара
class IsBuy(BoundFilter):
    async def check(self, message: types.Message):
        get_settings = get_settingsx()
        if get_settings[3] == "True" or str(message.from_user.id) in admins:
            return False
        else:
            return True


# Проверка на технические работы
class IsWork(BoundFilter):
    async def check(self, message: types.Message):
        get_settings = get_settingsx()
        if get_settings[2] == "True" or str(message.from_user.id) in admins:
            return False
        else:
            return True


# Проверка на технические работы
class IsUser(BoundFilter):
    async def check(self, message: types.Message):
        get_profile = get_userx(user_id=message.from_user.id)
        if get_profile is not None:
            return False
        else:
            return True
