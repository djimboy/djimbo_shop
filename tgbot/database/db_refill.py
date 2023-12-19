# - *- coding: utf- 8 - *-
import sqlite3
from typing import Union

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded


# Модель таблицы
class RefillModel(BaseModel):
    increment: int
    user_id: int
    refill_comment: str
    refill_amount: float
    refill_receipt: Union[str, int]
    refill_method: str
    refill_unix: int


# Работа с пополнениями
class Refillx:
    storage_name = "storage_refill"

    # Добавление записи
    @staticmethod
    def add(
            user_id: int,
            refill_comment: str,
            refill_amount: float,
            refill_receipt: Union[str, int],
            refill_method: str,
    ):
        refill_unix = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            con.execute(
                ded(f"""
                    INSERT INTO {Refillx.storage_name} (
                        user_id,
                        refill_comment,
                        refill_amount,
                        refill_receipt,
                        refill_method,
                        refill_unix
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """),
                [
                    user_id,
                    refill_comment,
                    refill_amount,
                    refill_receipt,
                    refill_method,
                    refill_unix,
                ],
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> RefillModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Refillx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = RefillModel(**response)

            return response

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[RefillModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Refillx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [RefillModel(**cache_object) for cache_object in response]

            return response

    # Получение всех записей
    @staticmethod
    def get_all() -> list[RefillModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Refillx.storage_name}"

            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [RefillModel(**cache_object) for cache_object in response]

            return response

    # Редактирование записи
    @staticmethod
    def update(refill_receipt, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Refillx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(refill_receipt)

            con.execute(sql + "WHERE refill_receipt = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Refillx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Refillx.storage_name}"

            con.execute(sql)
