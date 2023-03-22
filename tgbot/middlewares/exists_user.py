# - *- coding: utf- 8 - *-
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update

from tgbot.data.config import get_admins
from tgbot.services.api_sqlite import get_userx, add_userx, update_userx, get_settingsx
from tgbot.utils.const_functions import clear_html


# Проверка юзеров в БД и его добавление
class ExistsUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.prefix = "key_prefix"
        super(ExistsUserMiddleware, self).__init__()

    async def on_process_update(self, update: Update, data: dict):
        if "message" in update:
            get_update = update.message
        elif "callback_query" in update:
            get_update = update.callback_query
        else:
            get_update = None

        if get_update is not None and not get_update.from_user.is_bot:
            this_user = get_update.from_user
            get_prefix = self.prefix

            get_settings = get_settingsx()

            if get_settings['status_work'] == "False" or this_user.id in get_admins():
                get_user = get_userx(user_id=this_user.id)

                user_id = this_user.id
                user_login = this_user.username
                user_name = clear_html(this_user.first_name)
                user_surname = clear_html(this_user.last_name)
                user_fullname = clear_html(this_user.first_name)

                if user_login is None: user_login = ""
                if user_name is None: user_name = ""
                if user_surname is None: user_surname = ""
                if user_fullname is None: user_fullname = ""
                if len(user_surname) >= 1: user_fullname += f" {user_surname}"

                if get_user is None:
                    add_userx(user_id, user_login.lower(), user_name)
                else:
                    if user_fullname != get_user['user_name']:
                        update_userx(get_user['user_id'], user_name=user_fullname)

                    if user_login.lower() != get_user['user_login']:
                        update_userx(get_user['user_id'], user_login=user_login.lower())
