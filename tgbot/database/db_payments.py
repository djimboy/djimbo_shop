# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format


# Модель таблицы
class PaymentModel(BaseModel):
    qiwi_login: str
    qiwi_token: str
    yoomoney_token: str
    way_qiwi: str
    way_yoomoney: str


# Работа с платежными системами
class Paymentsx:
    storage_name = "storage_payment"

    # Получение записи
    @staticmethod
    def get() -> PaymentModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Paymentsx.storage_name}"

            return PaymentModel(**con.execute(sql).fetchone())

    # Редактирование записи
    @staticmethod
    def update(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Paymentsx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)

            con.execute(sql, parameters)
