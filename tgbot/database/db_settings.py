# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format


# Модель таблицы
class SettingsModel(BaseModel):
    status_work: str  # Статус работы бота (True - бот выключен, False - бот включён)
    status_refill: str  # Статус пополнений (True - включены, False - выключены)
    status_buy: str  # Статус покупок (True - включены, False - выключены)
    misc_faq: str  # Текст для FAQ
    misc_support: str  # Контакты поддержки
    misc_bot: str  # Юзернейм запускаемого бота
    misc_item_hide: str  # Статус отображения позиций без товаров (True - скрывать позиции, False - отображать)
    misc_profit_day: int  # UNIX время за День
    misc_profit_week: int  # UNIX время за Неделю
    misc_profit_month: int  # UNIX время за Месяц


# Работа с настройками
class Settingsx:
    storage_name = "storage_settings"

    # Получение записи
    @staticmethod
    def get() -> SettingsModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Settingsx.storage_name}"

            return SettingsModel(**con.execute(sql).fetchone())

    # Редактирование записи
    @staticmethod
    def update(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Settingsx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)

            con.execute(sql, parameters)
