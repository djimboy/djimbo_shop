# - *- coding: utf- 8 - *-
import time
import uuid
from datetime import datetime
from typing import Union

import pytz
from aiogram import Bot
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup

from tgbot.data.config import BOT_TIMEZONE, get_admins
from tgbot.utils.misc.bot_logging import bot_logger


################################### AIOGRAM ####################################
# Генерация реплай кнопки
def rkb(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)


# Генерация инлайн кнопки
def ikb(text: str, data: str = None, url: str = None) -> InlineKeyboardButton:
    if data is not None:
        return InlineKeyboardButton(text=text, callback_data=data)
    elif url is not None:
        return InlineKeyboardButton(text=text, url=url)


# Удаление сообщения с обработкой ошибок от телеграма
async def del_message(message: Message):
    try:
        await message.delete()
    except:
        ...


# Умная отправка сообщений (автоотправка сообщения с фото или без)
async def smart_message(
        bot: Bot,
        user_id: int,
        text: str,
        keyboard: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] = None,
        photo: Union[str, None] = None,
):
    if photo is not None and photo.title() != "None":
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=text,
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=keyboard,
        )


# Отправка сообщения всем админам
async def send_admins(bot: Bot, text: str, keyboard=None, not_me=0):
    for admin in get_admins():
        try:
            if str(admin) != str(not_me):
                await bot.send_message(
                    admin,
                    text,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                )
        except:
            ...


# Уведомление об ошибке
async def send_errors(bot: Bot, error_code: int):
    text_error = f"myError: {error_code}"

    print(text_error)
    bot_logger.warning(text_error)
    await send_admins(bot, text_error)


#################################### ПРОЧЕЕ ####################################
# Получение даты
def get_date(full: bool = True) -> str:
    if full:  # Полная дата с временем
        return datetime.now(pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
    else:  # Только дата без времени
        return datetime.now(pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y")


# Получение unix времени
def get_unix(full: bool = False) -> int:
    if full:  # Получение времени в наносекундах
        return time.time_ns()
    else:  # Получение времени в секундах
        return int(time.time())


# Удаление отступов у текста
def ded(get_text: str) -> str:
    if get_text is not None:
        split_text = get_text.split("\n")

        if split_text[0] == "": split_text.pop(0)
        if split_text[-1] == "": split_text.pop()
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
    while "." in get_list: get_list.remove(".")
    while "," in get_list: get_list.remove(",")
    while "\r" in get_list: get_list.remove("\r")
    while "\n" in get_list: get_list.remove("\n")

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


# Генерация уникального айди
def gen_id() -> int:
    mac_address = uuid.getnode()
    time_unix = int(str(time.time_ns())[:16])

    return mac_address + time_unix


# Конвертация unix в дату и даты в unix
def convert_date(from_time, full=True, second=True) -> Union[str, int]:
    from tgbot.data.config import BOT_TIMEZONE

    if "-" in str(from_time):
        from_time = from_time.replace("-", ".")

    if str(from_time).isdigit():
        if full:
            to_time = datetime.fromtimestamp(from_time, pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
        elif second:
            to_time = datetime.fromtimestamp(from_time, pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M")
        else:
            to_time = datetime.fromtimestamp(from_time, pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y")
    else:
        if " " in str(from_time):
            cache_time = from_time.split(" ")

            if ":" in cache_time[0]:
                cache_date = cache_time[1].split(".")
                cache_time = cache_time[0].split(":")
            else:
                cache_date = cache_time[0].split(".")
                cache_time = cache_time[1].split(":")

            if len(cache_date[0]) == 4:
                x_year, x_month, x_day = cache_date[0], cache_date[1], cache_date[2]
            else:
                x_year, x_month, x_day = cache_date[2], cache_date[1], cache_date[0]

            x_hour, x_minute, x_second = cache_time[0], cache_time[2], cache_time[2]

            from_time = f"{x_day}.{x_month}.{x_year} {x_hour}:{x_minute}:{x_second}"
        else:
            cache_date = from_time.split(".")

            if len(cache_date[0]) == 4:
                x_year, x_month, x_day = cache_date[0], cache_date[1], cache_date[2]
            else:
                x_year, x_month, x_day = cache_date[2], cache_date[1], cache_date[0]

            from_time = f"{x_day}.{x_month}.{x_year}"

        if " " in str(from_time):
            to_time = int(datetime.strptime(from_time, "%d.%m.%Y %H:%M:%S").timestamp())
        else:
            to_time = int(datetime.strptime(from_time, "%d.%m.%Y").timestamp())

    return to_time


##################################### ЧИСЛА ####################################
# Преобразование длинных вещественных чисел в читаемый вид
def snum(amount, remains=0) -> str:
    format_str = "{:." + str(remains) + "f}"
    str_amount = format_str.format(float(amount))

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
