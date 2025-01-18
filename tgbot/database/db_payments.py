# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format


# Модель таблицы
class PaymentsModel(BaseModel):
    cryptobot_token: str  # Криптобот токен
    yoomoney_token: str  # Юмани токен
    cryptocloud_token: str  # Cryptocloud токен
    cryptocloud_shop_id: str  # Cryptocloud shopid
    status_cryptobot: str  # Статус работы криптобота
    status_yoomoney: str  # Статус работы юмани
    status_cryptocloud: str # Статус работу cryptocloud


# Работа с платежными системами
class Paymentsx:
    storage_name = "storage_payments"

    # Получение записи
    @staticmethod
    def get() -> PaymentsModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Paymentsx.storage_name}"

            return PaymentsModel(**con.execute(sql).fetchone())

    # Редактирование записи
    @staticmethod
    def update(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Paymentsx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)

            con.execute(sql, parameters)
