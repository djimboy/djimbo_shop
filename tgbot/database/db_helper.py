# - *- coding: utf- 8 - *-
import sqlite3

from tgbot.data.config import PATH_DATABASE
from tgbot.utils.const_functions import get_unix, ded


# Преобразование полученного списка в словарь
def dict_factory(cursor, row) -> dict:
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


# Форматирование запроса без аргументов
def update_format(sql, parameters: dict) -> tuple[str, list]:
    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql += f" {values}"

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def update_format_where(sql, parameters: dict) -> tuple[str, list]:
    sql += " WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())


################################################################################
# Создание всех таблиц для БД
def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        ############################################################
        # Создание таблицы с хранением - Пользователей
        if len(con.execute("PRAGMA table_info(storage_users)").fetchall()) == 8:
            print("DB was found(1/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_users(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        user_login TEXT,
                        user_name TEXT,
                        user_balance REAL,
                        user_refill REAL,
                        user_give REAL,
                        user_unix INTEGER
                    )
                """)
            )
            print("DB was not found(1/8) | Creating...")

        # Создание таблицы с хранением - Настроек
        if len(con.execute("PRAGMA table_info(storage_settings)").fetchall()) == 13:
            print("DB was found(2/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_settings(
                        status_work TEXT,
                        status_refill TEXT,
                        status_buy TEXT,
                        misc_faq TEXT,
                        misc_support TEXT,
                        misc_bot TEXT,
                        misc_discord_webhook_url TEXT,
                        misc_discord_webhook_name TEXT,
                        misc_hide_category TEXT,
                        misc_hide_position TEXT,
                        misc_profit_day INTEGER,
                        misc_profit_week INTEGER,
                        misc_profit_month INTEGER
                    )
                """)
            )

            con.execute(
                ded(f"""
                    INSERT INTO storage_settings(
                        status_work,
                        status_refill,
                        status_buy,
                        misc_faq,
                        misc_support,
                        misc_bot,
                        misc_discord_webhook_url,
                        misc_discord_webhook_name,
                        misc_hide_category,
                        misc_hide_position,
                        misc_profit_day,
                        misc_profit_week,
                        misc_profit_month
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """),
                [
                    'True',
                    'False',
                    'False',
                    'None',
                    'None',
                    'None',
                    'None',
                    'None',
                    'False',
                    'False',
                    get_unix(),
                    get_unix(),
                    get_unix(),
                ]
            )
            print("DB was not found(2/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - Данных платежных систем
        if len(con.execute("PRAGMA table_info(storage_payments)").fetchall()) == 7:
            print("DB was found(3/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_payments(
                        cryptobot_token TEXT,
                        yoomoney_token TEXT,
                        cryptocloud_token TEXT,
                        cryptocloud_shop_id TEXT,
                        status_cryptobot TEXT,
                        status_yoomoney TEXT,
                        status_cryptocloud
                    )
                """)
            )

            con.execute(
                ded(f"""
                    INSERT INTO storage_payments(
                        cryptobot_token,
                        yoomoney_token,
                        cryptocloud_token,
                        cryptocloud_shop_id,
                        status_cryptobot,
                        status_yoomoney,
                        status_cryptocloud
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """),
                [
                    'None',
                    'None',
                    'None',
                    'None',
                    'False',
                    'False',
                    'False'
                ]
            )
            print("DB was not found(3/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - Пополнений пользователей
        if len(con.execute("PRAGMA table_info(storage_refill)").fetchall()) == 7:
            print("DB was found(4/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_refill(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        refill_comment TEXT,
                        refill_amount REAL,
                        refill_receipt TEXT,
                        refill_method TEXT,
                        refill_unix INTEGER
                    )
                """)
            )
            print("DB was not found(4/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - Категорий
        if len(con.execute("PRAGMA table_info(storage_category)").fetchall()) == 4:
            print("DB was found(5/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_category(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER,
                        category_name TEXT,
                        category_unix INTEGER
                    )
                """)
            )
            print("DB was not found(5/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - Позиций
        if len(con.execute("PRAGMA table_info(storage_position)").fetchall()) == 8:
            print("DB was found(6/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_position(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER,
                        position_id INTEGER,
                        position_name TEXT,
                        position_price REAL,
                        position_desc TEXT,
                        position_photo TEXT,
                        position_unix INTEGER
                    )
                """)
            )
            print("DB was not found(6/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - Товаров
        if len(con.execute("PRAGMA table_info(storage_item)").fetchall()) == 7:
            print("DB was found(7/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_item(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        category_id INTEGER,
                        position_id INTEGER,
                        item_id INTEGER,
                        item_unix INTEGER,
                        item_data TEXT
                    )
                """)
            )
            print("DB was not found(7/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - Покупок
        if len(con.execute("PRAGMA table_info(storage_purchases)").fetchall()) == 14:
            print("DB was found(8/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_purchases(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        user_balance_before REAL,
                        user_balance_after REAL,
                        purchase_receipt TEXT,
                        purchase_data TEXT,
                        purchase_count INTEGER,
                        purchase_price REAL,
                        purchase_price_one REAL,
                        purchase_position_id INTEGER,
                        purchase_position_name TEXT,
                        purchase_category_id INTEGER,
                        purchase_category_name TEXT,
                        purchase_unix INTEGER
                    )
                """)
            )
            print("DB was not found(8/8) | Creating...")
