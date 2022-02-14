# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class StorageFunctions(StatesGroup):
    here_search_profile = State()
    here_search_receipt = State()
    here_cache_user_id = State()
    here_send_message = State()
    here_add_balance = State()
    here_set_balance = State()
    here_ad_text = State()
