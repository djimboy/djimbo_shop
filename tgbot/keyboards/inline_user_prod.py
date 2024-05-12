# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.utils.const_functions import ikb


# Открытие позиции для просмотра
def products_open_finl(position_id: int, category_id: int, remover: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("💰 Купить товар", data=f"buy_item_open:{position_id}:{remover}"),
    ).row(
        ikb("🔙 Вернуться", data=f"buy_category_open:{category_id}:{remover}"),
    )

    return keyboard.as_markup()


# Подтверждение покупки товара
def products_confirm_finl(position_id: int, category_id: int, get_count: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Подтвердить", data=f"buy_item_confirm:{position_id}:{get_count}"),
        ikb("❌ Отменить", data=f"buy_position_open:{position_id}:0"),
    )

    return keyboard.as_markup()


# Возврат к позиции при отмене ввода
def products_return_finl(position_id: int, category_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🔙 Вернуться", data=f"buy_position_open:{position_id}:0"),
    )

    return keyboard.as_markup()
