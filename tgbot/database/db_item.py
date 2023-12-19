# - *- coding: utf- 8 - *-
import math
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import ded, clear_list, gen_id, get_unix, clear_html


# Модель таблицы
class ItemModel(BaseModel):
    user_id: int
    category_id: int
    position_id: int
    item_id: int
    item_unix: int
    item_data: str


# Работа с категориями
class Itemx:
    storage_name = "storage_item"

    # Добавление записей
    @staticmethod
    def add(
            user_id: int,
            category_id: int,
            position_id: int,
            item_datas: list[str],
    ):
        item_unix = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            item_datas = clear_list(item_datas)

            for item_data in item_datas:
                item_id = gen_id()
                item_data = clear_html(item_data.strip())

                con.execute(
                    ded(f"""
                        INSERT INTO {Itemx.storage_name} (
                            user_id,
                            category_id,
                            position_id,
                            item_id,
                            item_unix,
                            item_data
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """),
                    [
                        user_id,
                        category_id,
                        position_id,
                        item_id,
                        item_unix,
                        item_data,
                    ],
                )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> ItemModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Itemx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = ItemModel(**response)

            return response

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[ItemModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Itemx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [ItemModel(**cache_object) for cache_object in response]

            return response

    # Получение всех записей
    @staticmethod
    def get_all() -> list[ItemModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Itemx.storage_name}"

            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [ItemModel(**cache_object) for cache_object in response]

            return response

    # Редактирование записи
    @staticmethod
    def update(item_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Itemx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(item_id)

            con.execute(sql + "WHERE item_id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Itemx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Itemx.storage_name}"

            con.execute(sql)

    # Покупка товара
    @staticmethod
    def buy(get_items: list[ItemModel], count: int) -> tuple[list[str], int]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            save_items, save_len = [], 0

            for x, select_item in enumerate(get_items):
                if x != count:
                    if count > 1:
                        select_data = f"{x + 1}. {select_item.item_data}"
                    else:
                        select_data = select_item.item_data

                    save_items.append(select_data)
                    sql, parameters = update_format_where(
                        f"DELETE FROM {Itemx.storage_name}",
                        {"item_id": select_item.item_id},
                    )
                    con.execute(sql, parameters)

                    if len(select_data) >= save_len:
                        save_len = len(select_data)
                else:
                    break

            save_len = math.ceil(3500 / (save_len + 1))

        return save_items, save_len
