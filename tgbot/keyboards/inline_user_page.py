# - *- coding: utf- 8 - *-

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_category import Categoryx
from tgbot.database.db_item import Itemx
from tgbot.keyboards.inline_helper import build_pagination_finl
from tgbot.utils.const_functions import ikb
from tgbot.utils.misc_functions import get_positions_items


# fp - flip page


################################################################################
################################ ПОКУПКИ ТОВАРОВ ###############################
# Страницы категорий при покупке товара
def prod_item_category_swipe_fp(remover: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_categories = Categoryx.get_all()

    for count, select in enumerate(range(remover, len(get_categories))):
        if count < 10:
            category = get_categories[select]

            keyboard.row(
                ikb(
                    category.category_name,
                    data=f"buy_category_open:{category.category_id}:0",
                )
            )

    buildp_kb = build_pagination_finl(get_categories, f"buy_category_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


# Страницы позиций для покупки товаров
def prod_item_position_swipe_fp(remover: int, category_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_positions = get_positions_items(category_id)

    for count, select in enumerate(range(remover, len(get_positions))):
        if count < 10:
            position = get_positions[select]
            get_items = Itemx.gets(position_id=get_positions[select].position_id)

            keyboard.row(
                ikb(
                    f"{position.position_name} | {position.position_price}₽ | {len(get_items)} шт",
                    data=f"buy_position_open:{position.position_id}:{remover}",
                )
            )

    buildp_kb = build_pagination_finl(get_positions, f"buy_position_swipe:{category_id}", remover)
    keyboard.row(*buildp_kb)

    keyboard.row(ikb("🔙 Вернуться", data=f"buy_category_swipe:0"))

    return keyboard.as_markup()


################################################################################
################################ НАЛИЧИЕ ТОВАРОВ ###############################
# Страницы наличия товаров
def prod_available_swipe_fp(remover_now: int, remover_max: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    if remover_max > 1:
        if remover_now > 1 and remover_max >= 3:
            keyboard.add(
                ikb("⏪", data=f"user_available_swipe:{0}"),
            )

        if remover_now >= 1:
            keyboard.add(
                ikb("⬅️", data=f"user_available_swipe:{remover_now - 1}"),
            )

        keyboard.add(
            ikb(f"{remover_now + 1}/{remover_max}", data="...")
        )

        if remover_now + 1 < remover_max:
            keyboard.add(
                ikb("➡️", data=f"user_available_swipe:{remover_now + 1}"),
            )

        if remover_now + 1 < remover_max - 1 and remover_max >= 3:
            keyboard.add(
                ikb("⏩", data=f"user_available_swipe:{remover_max - 1}"),
            )

        keyboard.adjust(5)

    return keyboard.as_markup()
