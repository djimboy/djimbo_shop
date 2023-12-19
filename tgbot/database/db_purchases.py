# - *- coding: utf- 8 - *-
import sqlite3
from typing import Union

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import ded, get_unix


# Модель таблицы
class PurchasesModel(BaseModel):
    increment: int
    user_id: int
    user_balance_before: float
    user_balance_after: float
    purchase_receipt: Union[str, int]
    purchase_data: str
    purchase_count: int
    purchase_price: float
    purchase_price_one: float
    purchase_position_id: int
    purchase_position_name: str
    purchase_category_id: int
    purchase_category_name: str
    purchase_unix: int


# Работа с категориями
class Purchasesx:
    storage_name = "storage_purchases"

    # Добавление записи
    @staticmethod
    def add(
            user_id: int,
            user_balance_before: float,
            user_balance_after: float,
            purchase_receipt: Union[str, int],
            purchase_data: str,
            purchase_count: int,
            purchase_price: float,
            purchase_price_one: float,
            purchase_position_id: int,
            purchase_position_name: str,
            purchase_category_id: int,
            purchase_category_name: str,
    ):
        purchase_unix = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            con.execute(
                ded(f"""
                    INSERT INTO {Purchasesx.storage_name} (
                        user_id,
                        user_balance_before,
                        user_balance_after,
                        purchase_receipt,
                        purchase_data,
                        purchase_count,
                        purchase_price,
                        purchase_price_one,
                        purchase_position_id,
                        purchase_position_name,
                        purchase_category_id,
                        purchase_category_name,
                        purchase_unix
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """),
                [
                    user_id,
                    user_balance_before,
                    user_balance_after,
                    purchase_receipt,
                    purchase_data,
                    purchase_count,
                    purchase_price,
                    purchase_price_one,
                    purchase_position_id,
                    purchase_position_name,
                    purchase_category_id,
                    purchase_category_name,
                    purchase_unix,
                ],
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> PurchasesModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Purchasesx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = PurchasesModel(**response)

            return response

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[PurchasesModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Purchasesx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [PurchasesModel(**cache_object) for cache_object in response]

            return response

    # Получение всех записей
    @staticmethod
    def get_all() -> list[PurchasesModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Purchasesx.storage_name}"

            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [PurchasesModel(**cache_object) for cache_object in response]

            return response

    # Редактирование записи
    @staticmethod
    def update(purchase_receipt, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Purchasesx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(purchase_receipt)

            con.execute(sql + "WHERE purchase_receipt = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Purchasesx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Purchasesx.storage_name}"

            con.execute(sql)
