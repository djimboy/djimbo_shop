# - *- coding: utf- 8 - *-
import time
from datetime import datetime
from typing import Union

import pytz

from tgbot.data.config import BOT_TIMEZONE


######################################## ПРОЧЕЕ ########################################
# Получение даты
def get_date(full: bool = True) -> str:
    if full:  # Полная дата с временем
        return datetime.now(pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
    else:  # Только дата без времени
        return datetime.now(pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y")


# Получение unix времени
def get_unix(full: bool = False) -> int:
    if full:
        return time.time_ns()
    else:
        return int(time.time())


# Удаление отступов у текста
def ded(get_text: str) -> str:
    if get_text is not None:
        split_text = get_text.split("\n")

        if split_text[0] == "": split_text.pop(0)
        if split_text[-1] == "": split_text.pop(-1)
        save_text = []

        for text in split_text:
            while text.startswith(" "):
                text = text[1:]

            save_text.append(text)
        get_text = "\n".join(save_text)
    else:
        get_text = ""

    return get_text


# Очистка текста от HTML тэгов
def clear_html(get_text: str) -> str:
    if get_text is not None:
        if "<" in get_text: get_text = get_text.replace("<", "*")
        if ">" in get_text: get_text = get_text.replace(">", "*")
    else:
        get_text = ""

    return get_text


# Очистка мусорных символов из списка
def clear_list(get_list: list) -> list:
    while "" in get_list: get_list.remove("")
    while " " in get_list: get_list.remove(" ")
    while "," in get_list: get_list.remove(",")
    while "\r" in get_list: get_list.remove("\r")

    return get_list


# Разбив списка на несколько частей
def split_messages(get_list: list, count: int) -> list[list]:
    return [get_list[i:i + count] for i in range(0, len(get_list), count)]


# Конвертация дней
def convert_day(day: int) -> str:
    day = int(day)
    days = ['день', 'дня', 'дней']

    if day % 10 == 1 and day % 100 != 11:
        count = 0
    elif 2 <= day % 10 <= 4 and (day % 100 < 10 or day % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{day} {days[count]}"


######################################## ЧИСЛА ########################################
# Преобразование длинных вещественных чисел в читаемый вид
def snum(amount, remains=0) -> str:
    str_amount = f"{float(amount):8f}"

    if remains != 0:
        if "." in str_amount:
            remains_find = str_amount.find(".")
            remains_save = remains_find + 8 - (8 - remains) + 1

            str_amount = str_amount[:remains_save]

    if "." in str(str_amount):
        while str(str_amount).endswith('0'): str_amount = str(str_amount)[:-1]

    if str(str_amount).endswith('.'): str_amount = str(str_amount)[:-1]

    return str(str_amount)


# Конвертация числа в вещественное
def to_number(get_number, remains=2) -> Union[int, float]:
    if "," in str(get_number):
        get_number = str(get_number).replace(",", ".")

    if "." in str(get_number):
        get_last = str(get_number).split(".")

        if str(get_last[1]).endswith("0"):
            while True:
                if str(get_number).endswith("0"):
                    get_number = str(get_number)[:-1]
                else:
                    break

        get_number = round(float(get_number), remains)

    str_number = snum(get_number)
    if "." in str_number:
        if str_number.split(".")[1] == "0":
            get_number = int(get_number)
        else:
            get_number = float(get_number)
    else:
        get_number = int(get_number)

    return get_number


# Проверка числа на вещественное
def is_number(get_number) -> bool:
    if str(get_number).isdigit():
        return True
    else:
        if "," in str(get_number):
            get_number = str(get_number).replace(",", ".")

        try:
            float(get_number)
            return True
        except ValueError:
            return False
