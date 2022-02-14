# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class StorageSettings(StatesGroup):
    here_contact = State()
    here_faq = State()

