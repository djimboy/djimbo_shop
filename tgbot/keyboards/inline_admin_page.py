# - *- coding: utf- 8 - *-
import math

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_category import Categoryx
from tgbot.database.db_item import Itemx
from tgbot.database.db_position import Positionx
from tgbot.utils.const_functions import ikb


# fp - flip page

################################################################################
############################## ИЗМЕНЕНИЕ КАТЕГОРИИ #############################
# Cтраницы выбора категории для изменения
def category_edit_swipe_fp(remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()
    if 10 - (len(get_categories) % 10) != 10:
        remover_page = len(get_categories) + (10 - (len(get_categories) % 10))
    else:
        remover_page = len(get_categories)

    if remover >= len(get_categories): remover -= 10

    for count, a in enumerate(range(remover, len(get_categories))):
        if count < 10:
            keyboard.row(
                ikb(
                    get_categories[a].category_name,
                    data=f"category_edit_open:{get_categories[a].category_id}:{remover}",
                )
            )

    if len(get_categories) <= 10:
        ...
    elif len(get_categories) > 10 and remover < 10:
        if len(get_categories) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"catategory_edit_swipe:{remover + 10}"),
                ikb("⏩", data=f"catategory_edit_swipe:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"catategory_edit_swipe:{remover + 10}")
            )
    elif remover + 10 >= len(get_categories):
        if len(get_categories) > 20:
            keyboard.row(
                ikb("⏪", data=f"catategory_edit_swipe:0"),
                ikb("⬅️", data=f"catategory_edit_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"catategory_edit_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="...")
            )
    else:
        if len(get_categories) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"catategory_edit_swipe:0"),
                    ikb("⬅️", data=f"catategory_edit_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"catategory_edit_swipe:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"catategory_edit_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"catategory_edit_swipe:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"catategory_edit_swipe:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"catategory_edit_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"catategory_edit_swipe:{remover + 10}"),
            )

    return keyboard.as_markup()


################################################################################
################################ СОЗДАНИЕ ПОЗИЦИИ ##############################
# Страницы выбора категории для позиции
def position_add_swipe_fp(remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()
    if (10 - (len(get_categories) % 10)) != 10:
        remover_page = len(get_categories) + (10 - (len(get_categories) % 10))
    else:
        remover_page = len(get_categories)

    if remover >= len(get_categories): remover -= 10

    for count, a in enumerate(range(remover, len(get_categories))):
        if count < 10:
            keyboard.row(
                ikb(
                    get_categories[a].category_name,
                    data=f"position_add_open:{get_categories[a].category_id}",
                )
            )

    if len(get_categories) <= 10:
        ...
    elif len(get_categories) > 10 and remover < 10:
        if len(get_categories) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"position_add_swipe:{remover + 10}"),
                ikb("⏩", data=f"position_add_swipe:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"position_add_swipe:{remover + 10}"),
            )
    elif remover + 10 >= len(get_categories):
        if len(get_categories) > 20:
            keyboard.row(
                ikb("⏪", data=f"position_add_swipe:0"),
                ikb("⬅️", data=f"position_add_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"position_add_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
            )
    else:
        if len(get_categories) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"position_add_swipe:0"),
                    ikb("⬅️", data=f"position_add_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"position_add_swipe:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"position_add_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"position_add_swipe:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"position_add_swipe:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"position_add_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"position_add_swipe:{remover + 10}"),
            )

    return keyboard.as_markup()


################################################################################
############################### ИЗМЕНЕНИЕ ПОЗИЦИИ ##############################
# Cтраницы категорий для изменения позиции
def position_edit_category_swipe_fp(remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()
    if (10 - (len(get_categories) % 10)) != 10:
        remover_page = len(get_categories) + (10 - (len(get_categories) % 10))
    else:
        remover_page = len(get_categories)

    if remover >= len(get_categories): remover -= 10

    for count, a in enumerate(range(remover, len(get_categories))):
        if count < 10:
            keyboard.row(
                ikb(
                    get_categories[a].category_name,
                    data=f"position_edit_category_open:{get_categories[a].category_id}"
                )
            )

    if len(get_categories) <= 10:
        ...
    elif len(get_categories) > 10 and remover < 10:
        if len(get_categories) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"position_edit_category_swipe:{remover + 10}"),
                ikb("⏩", data=f"position_edit_category_swipe:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"position_edit_category_swipe:{remover + 10}")
            )
    elif remover + 10 >= len(get_categories):
        if len(get_categories) > 20:
            keyboard.row(
                ikb("⏪", data=f"position_edit_category_swipe:0"),
                ikb("⬅️", data=f"position_edit_category_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"position_edit_category_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="...")
            )
    else:
        if len(get_categories) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"position_edit_category_swipe:0"),
                    ikb("⬅️", data=f"position_edit_category_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"position_edit_category_swipe:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"position_edit_category_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"position_edit_category_swipe:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"position_edit_category_swipe:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"position_edit_category_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"position_edit_category_swipe:{remover + 10}"),
            )

    return keyboard.as_markup()


# Cтраницы выбора позиции для изменения
def position_edit_swipe_fp(remover, category_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_positions = Positionx.gets(category_id=category_id)
    if 10 - (len(get_positions) % 10) != 10:
        remover_page = len(get_positions) + (10 - (len(get_positions) % 10))
    else:
        remover_page = len(get_positions)

    if remover >= len(get_positions): remover -= 10

    for count, a in enumerate(range(remover, len(get_positions))):
        if count < 10:
            get_items = Itemx.gets(position_id=get_positions[a].position_id)

            keyboard.row(
                ikb(
                    f"{get_positions[a].position_name} | {get_positions[a].position_price}₽ | {len(get_items)} шт",
                    data=f"position_edit_open:{get_positions[a].position_id}:{category_id}:{remover}",
                )
            )

    if len(get_positions) <= 10:
        ...
    elif len(get_positions) > 10 and remover < 10:
        if len(get_positions) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_positions) / 10)}", data="..."),
                ikb("➡️", data=f"position_edit_swipe:{category_id}:{remover + 10}"),
                ikb("⏩", data=f"position_edit_swipe:{category_id}:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_positions) / 10)}", data="..."),
                ikb("➡️", data=f"position_edit_swipe:{category_id}:{remover + 10}")
            )
    elif remover + 10 >= len(get_positions):
        if len(get_positions) > 20:
            keyboard.row(
                ikb("⏪", data=f"position_edit_swipe:{category_id}:0"),
                ikb("⬅️", data=f"position_edit_swipe:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"position_edit_swipe:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="...")
            )
    else:
        if len(get_positions) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"position_edit_swipe:{category_id}:0"),
                    ikb("⬅️", data=f"position_edit_swipe:{category_id}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
                    ikb("➡️", data=f"position_edit_swipe:{category_id}:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"position_edit_swipe:{category_id}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
                    ikb("➡️", data=f"position_edit_swipe:{category_id}:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"position_edit_swipe:{category_id}:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"position_edit_swipe:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
                ikb("➡️", data=f"position_edit_swipe:{category_id}:{remover + 10}"),
            )

    keyboard.row(ikb("🔙 Вернуться", data="position_edit_category_swipe:0"))

    return keyboard.as_markup()


################################################################################
############################### ДОБАВЛЕНИЕ ТОВАРОВ #############################
# Страницы категорий для добавления товаров
def item_add_category_swipe_fp(remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()
    if (10 - (len(get_categories) % 10)) != 10:
        remover_page = len(get_categories) + (10 - (len(get_categories) % 10))
    else:
        remover_page = len(get_categories)

    if remover >= len(get_categories): remover -= 10

    for count, a in enumerate(range(remover, len(get_categories))):
        if count < 10:
            keyboard.row(
                ikb(
                    get_categories[a].category_name,
                    data=f"item_add_category_open:{get_categories[a].category_id}:{remover}",
                )
            )

    if len(get_categories) <= 10:
        ...
    elif len(get_categories) > 10 and remover < 10:
        if len(get_categories) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"item_add_category_swipe:{remover + 10}"),
                ikb("⏩", data=f"item_add_category_swipe:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"item_add_category_swipe:{remover + 10}"),
            )
    elif remover + 10 >= len(get_categories):
        if len(get_categories) > 20:
            keyboard.row(
                ikb("⏪", data=f"item_add_category_swipe:0"),
                ikb("⬅️", data=f"item_add_category_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"item_add_category_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
            )
    else:
        if len(get_categories) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"item_add_category_swipe:0"),
                    ikb("⬅️", data=f"item_add_category_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"item_add_category_swipe:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"item_add_category_swipe:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                    ikb("➡️", data=f"item_add_category_swipe:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"item_add_category_swipe:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"item_add_category_swipe:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_categories) / 10)}", data="..."),
                ikb("➡️", data=f"item_add_category_swipe:{remover + 10}"),
            )

    return keyboard.as_markup()


# Страницы позиций для добавления товаров
def item_add_position_swipe_fp(remover, category_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_positions = Positionx.gets(category_id=category_id)
    if 10 - (len(get_positions) % 10) != 10:
        remover_page = len(get_positions) + (10 - (len(get_positions) % 10))
    else:
        remover_page = len(get_positions)

    if remover >= len(get_positions): remover -= 10

    for count, a in enumerate(range(remover, len(get_positions))):
        if count < 10:
            get_items = Itemx.gets(position_id=get_positions[a].position_id)

            keyboard.row(
                ikb(
                    f"{get_positions[a].position_name} | {get_positions[a].position_price}₽ | {len(get_items)} шт",
                    data=f"item_add_position_open:{get_positions[a].position_id}:{category_id}",
                )
            )

    if len(get_positions) <= 10:
        ...
    elif len(get_positions) > 10 and remover < 10:
        if len(get_positions) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_positions) / 10)}", data="..."),
                ikb("➡️", data=f"item_add_position_swipe:{category_id}:{remover + 10}"),
                ikb("⏩", data=f"item_add_position_swipe:{category_id}:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_positions) / 10)}", data="..."),
                ikb("➡️", data=f"item_add_position_swipe:{category_id}:{remover + 10}")
            )
    elif remover + 10 >= len(get_positions):
        if len(get_positions) > 20:
            keyboard.row(
                ikb("⏪", data=f"item_add_position_swipe:{category_id}:0"),
                ikb("⬅️", data=f"item_add_position_swipe:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"item_add_position_swipe:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="...")
            )
    else:
        if len(get_positions) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"item_add_position_swipe:{category_id}:0"),
                    ikb("⬅️", data=f"item_add_position_swipe:{category_id}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
                    ikb("➡️", data=f"item_add_position_swipe:{category_id}:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"item_add_position_swipe:{category_id}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
                    ikb("➡️", data=f"item_add_position_swipe:{category_id}:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"item_add_position_swipe:{category_id}:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"item_add_position_swipe:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_positions) / 10)}", data="..."),
                ikb("➡️", data=f"item_add_position_swipe:{category_id}:{remover + 10}"),
            )

    keyboard.row(ikb("🔙 Вернуться", data="products_add_category_swipe:0"))

    return keyboard.as_markup()


################################################################################
################################ УДАЛЕНИЕ ТОВАРОВ ##############################
# Страницы товаров для удаления
def item_delete_swipe_fp(remover, position_id, category_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_items = Itemx.gets(position_id=position_id)
    if 10 - (len(get_items) % 10) != 10:
        remover_page = len(get_items) + (10 - (len(get_items) % 10))
    else:
        remover_page = len(get_items)

    if remover >= len(get_items): remover -= 10

    for count, a in enumerate(range(remover, len(get_items))):
        if count < 10:
            keyboard.row(
                ikb(
                    get_items[a].item_data,
                    data=f"item_delete_open:{get_items[a].item_id}",
                )
            )

    if len(get_items) <= 10:
        ...
    elif len(get_items) > 10 and remover < 10:
        if len(get_items) > 20:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_items) / 10)}", data="..."),
                ikb("➡️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover + 10}"),
                ikb("⏩", data=f"item_delete_swipe:{position_id}:{category_id}:{remover_page}"),
            )
        else:
            keyboard.row(
                ikb(f"1/{math.ceil(len(get_items) / 10)}", data="..."),
                ikb("➡️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover + 10}")
            )
    elif remover + 10 >= len(get_items):
        if len(get_items) > 20:
            keyboard.row(
                ikb("⏪", data=f"item_delete_swipe:{position_id}:{category_id}:0"),
                ikb("⬅️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_items) / 10)}", data="..."),
            )
        else:
            keyboard.row(
                ikb("⬅️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_items) / 10)}", data="...")
            )
    else:
        if len(get_items) > 20:
            if remover >= 20:
                keyboard.row(
                    ikb("⏪", data=f"item_delete_swipe:{position_id}:{category_id}:0"),
                    ikb("⬅️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_items) / 10)}", data="..."),
                    ikb("➡️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover + 10}"),
                )
            else:
                keyboard.row(
                    ikb("⬅️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover - 10}"),
                    ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_items) / 10)}", data="..."),
                    ikb("➡️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover + 10}"),
                )

            if remover_page - 20 > remover:
                keyboard.add(
                    ikb("⏩", data=f"item_delete_swipe:{position_id}:{category_id}:{remover_page}"),
                )
        else:
            keyboard.row(
                ikb("⬅️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover - 10}"),
                ikb(f"{str(remover + 10)[:-1]}/{math.ceil(len(get_items) / 10)}", data="..."),
                ikb("➡️", data=f"item_delete_swipe:{position_id}:{category_id}:{remover + 10}"),
            )

    keyboard.row(ikb("🔙 Вернуться", data=f"position_edit_open:{position_id}:{category_id}:0"))

    return keyboard.as_markup()
