# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import ded, get_unix


# Модель таблицы
class PositionModel(BaseModel):
    increment: int
    category_id: int
    position_id: int
    position_name: str
    position_price: float
    position_desc: str
    position_photo: str
    position_unix: int


# Работа с категориями
class Positionx:
    storage_name = "storage_position"

    # Добавление записи
    @staticmethod
    def add(
            category_id: int,
            position_id: int,
            position_name: str,
            position_price: float,
            position_desc: str,
            position_photo: str,
    ):
        position_unix = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            con.execute(
                ded(f"""
                    INSERT INTO {Positionx.storage_name} (
                        position_id,
                        position_name,
                        position_price,
                        position_desc,
                        position_photo,
                        position_unix,
                        category_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """),
                [
                    position_id,
                    position_name,
                    position_price,
                    position_desc,
                    position_photo,
                    position_unix,
                    category_id,
                ],
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> PositionModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Positionx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = PositionModel(**response)

            return response

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[PositionModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Positionx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [PositionModel(**cache_object) for cache_object in response]

            return response

    # Получение всех записей
    @staticmethod
    def get_all() -> list[PositionModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Positionx.storage_name}"

            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [PositionModel(**cache_object) for cache_object in response]

            return response

    # Редактирование записи
    @staticmethod
    def update(position_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Positionx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(position_id)

            con.execute(sql + "WHERE position_id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Positionx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Positionx.storage_name}"

            con.execute(sql)
