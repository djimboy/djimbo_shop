# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class StorageUsers(StatesGroup):
    here_input_count_buy_item = State()
    here_cache_position_id = State()
    here_cache_count_item = State()
