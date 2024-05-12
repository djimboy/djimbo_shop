# - *- coding: utf- 8 - *-
import math

from aiogram.types import InlineKeyboardButton

from tgbot.utils.const_functions import ikb


# Генерация пагинации страниц
def build_pagination_finl(
        get_list: list,
        button_data: str,
        remover: int,
) -> list[InlineKeyboardButton]:
    save_kb = []

    if len(get_list) % 10 == 0:
        remover_page = len(get_list)
    else:
        remover_page = len(get_list) - len(get_list) % 10

    if len(get_list) % 10 == 0 and remover_page == len(get_list):
        remover_page -= 10

    if remover >= len(get_list): remover -= 10
    if remover < 0: remover = 0

    if len(get_list) <= 10:
        ...
    elif len(get_list) > 10 and remover < 10:
        if len(get_list) > 20:
            save_kb += [
                ikb(f"1/{math.ceil(len(get_list) / 10)}", data="..."),
                ikb("➡️", data=f"{button_data}:{remover + 10}"),
                ikb("⏩", data=f"{button_data}:{remover_page}"),
            ]
        else:
            save_kb += [
                ikb(f"1/{math.ceil(len(get_list) / 10)}", data="..."),
                ikb("➡️", data=f"{button_data}:{remover + 10}"),
            ]
    elif remover + 10 >= len(get_list):
        if len(get_list) > 20:
            save_kb += [
                ikb("⏪", data=f"{button_data}:0"),
                ikb("⬅️", data=f"{button_data}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_list) / 10)}", data="..."),
            ]
        else:
            save_kb += [
                ikb("⬅️", data=f"{button_data}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_list) / 10)}", data="..."),
            ]
    else:
        if len(get_list) > 20:
            if remover >= 20:
                save_kb += [
                    ikb("⏪", data=f"{button_data}:0"),
                    ikb("⬅️", data=f"{button_data}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_list) / 10)}", data="..."),
                    ikb("➡️", data=f"{button_data}:{remover + 10}"),
                ]
            else:
                save_kb += [
                    ikb("⬅️", data=f"{button_data}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_list) / 10)}", data="..."),
                    ikb("➡️", data=f"{button_data}:{remover + 10}"),
                ]

            if remover_page - 10 > remover:
                save_kb += [
                    ikb("⏩", data=f"{button_data}:{remover_page}"),
                ]
        else:
            save_kb += [
                ikb("⬅️", data=f"{button_data}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_list) / 10)}", data="..."),
                ikb("➡️", data=f"{button_data}:{remover + 10}"),
            ]

    return save_kb
