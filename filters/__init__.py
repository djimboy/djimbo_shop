from aiogram import Dispatcher

from .all_filters import IsPrivate
from .all_filters import IsAdmin
from .all_filters import IsWork
from .all_filters import IsUser


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsPrivate)
