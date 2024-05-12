# - *- coding: utf- 8 - *-
import math

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_category import Categoryx
from tgbot.database.db_item import Itemx
from tgbot.database.db_position import Positionx
from tgbot.keyboards.inline_helper import build_pagination_finl
from tgbot.utils.const_functions import ikb


# fp - flip page

################################################################################
############################## ИЗМЕНЕНИЕ КАТЕГОРИИ #############################
# Cтраницы выбора категории для изменения
def category_edit_swipe_fp(remover: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()

    for count, select in enumerate(range(remover, len(get_categories))):
        if count < 10:
            category = get_categories[select]

            keyboard.row(
                ikb(
                    category.category_name,
                    data=f"category_edit_open:{category.category_id}:{remover}",
                )
            )

    buildp_kb = build_pagination_finl(get_categories, f"category_edit_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


################################################################################
################################ СОЗДАНИЕ ПОЗИЦИИ ##############################
# Страницы выбора категории для позиции
def position_add_swipe_fp(remover: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()

    for count, select in enumerate(range(remover, len(get_categories))):
        if count < 10:
            category = get_categories[select]

            keyboard.row(
                ikb(
                    category.category_name,
                    data=f"position_add_open:{category.category_id}",
                )
            )

    buildp_kb = build_pagination_finl(get_categories, f"position_add_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


################################################################################
############################### ИЗМЕНЕНИЕ ПОЗИЦИИ ##############################
# Cтраницы категорий для изменения позиции
def position_edit_category_swipe_fp(remover: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()

    for count, select in enumerate(range(remover, len(get_categories))):
        if count < 10:
            category = get_categories[select]

            keyboard.row(
                ikb(
                    category.category_name,
                    data=f"position_edit_category_open:{category.category_id}"
                )
            )

    buildp_kb = build_pagination_finl(get_categories, f"position_edit_category_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


# Cтраницы выбора позиции для изменения
def position_edit_swipe_fp(remover: int, category_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_positions = Positionx.gets(category_id=category_id)

    for count, select in enumerate(range(remover, len(get_positions))):
        if count < 10:
            position = get_positions[select]
            get_items = Itemx.gets(position_id=get_positions[select].position_id)

            keyboard.row(
                ikb(
                    f"{position.position_name} | {position.position_price}₽ | {len(get_items)} шт",
                    data=f"position_edit_open:{position.position_id}:{category_id}:{remover}",
                )
            )

    buildp_kb = build_pagination_finl(get_positions, f"position_edit_swipe:{category_id}", remover)
    keyboard.row(*buildp_kb)

    keyboard.row(ikb("🔙 Вернуться", data="position_edit_category_swipe:0"))

    return keyboard.as_markup()


################################################################################
############################### ДОБАВЛЕНИЕ ТОВАРОВ #############################
# Страницы категорий для добавления товаров
def item_add_category_swipe_fp(remover: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()

    for count, select in enumerate(range(remover, len(get_categories))):
        if count < 10:
            category = get_categories[select]

            keyboard.row(
                ikb(
                    category.category_name,
                    data=f"item_add_category_open:{category.category_id}:{remover}",
                )
            )

    buildp_kb = build_pagination_finl(get_categories, f"item_add_category_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


# Страницы позиций для добавления товаров
def item_add_position_swipe_fp(remover: int, category_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_positions = Positionx.gets(category_id=category_id)

    for count, select in enumerate(range(remover, len(get_positions))):
        if count < 10:
            position = get_positions[select]
            get_items = Itemx.gets(position_id=get_positions[select].position_id)

            keyboard.row(
                ikb(
                    f"{position.position_name} | {position.position_price}₽ | {len(get_items)} шт",
                    data=f"item_add_position_open:{position.position_id}:{category_id}",
                )
            )

    buildp_kb = build_pagination_finl(get_positions, f"item_add_position_swipe:{category_id}", remover)
    keyboard.row(*buildp_kb)

    keyboard.row(ikb("🔙 Вернуться", data="products_add_category_swipe:0"))

    return keyboard.as_markup()


################################################################################
################################ УДАЛЕНИЕ ТОВАРОВ ##############################
# Страницы товаров для удаления
def item_delete_swipe_fp(remover: int, position_id: int, category_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_items = Itemx.gets(position_id=position_id)

    for count, select in enumerate(range(remover, len(get_items))):
        if count < 10:
            item = get_items[select]

            keyboard.row(
                ikb(
                    item.item_data,
                    data=f"item_delete_open:{item.item_id}",
                )
            )

    buildp_kb = build_pagination_finl(get_items, f"item_delete_swipe:{position_id}:{category_id}", remover)
    keyboard.row(*buildp_kb)

    keyboard.row(ikb("🔙 Вернуться", data=f"position_edit_open:{position_id}:{category_id}:0"))

    return keyboard.as_markup()
