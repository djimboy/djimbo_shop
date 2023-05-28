# - *- coding: utf- 8 - *-
from typing import Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as ikb

from tgbot.services.api_sqlite import get_paymentx


# Выбор способов пополнения
def refill_select_finl() -> Union[InlineKeyboardMarkup, None]:
    keyboard = InlineKeyboardMarkup()

    get_payments = get_paymentx()
    active_kb = []

    if get_payments['way_form'] == "True":
        active_kb.append(ikb("📋 QIWI форма", callback_data="refill_select:Form"))
    if get_payments['way_number'] == "True":
        active_kb.append(ikb("📞 QIWI номер", callback_data="refill_select:Number"))
    if get_payments['way_nickname'] == "True":
        active_kb.append(ikb("Ⓜ QIWI никнейм", callback_data="refill_select:Nickname"))

    if len(active_kb) == 3:
        keyboard.add(active_kb[0], active_kb[1])
        keyboard.add(active_kb[2])
    elif len(active_kb) == 2:
        keyboard.add(active_kb[0], active_kb[1])
    elif len(active_kb) == 1:
        keyboard.add(active_kb[0])
    else:
        keyboard = None

    if len(active_kb) >= 1:
        keyboard.add(ikb("🔙 Вернуться", callback_data="user_profile"))

    return keyboard


# Проверка киви платежа
def refill_bill_finl(send_requests, get_receipt, get_way) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        ikb("🌀 Перейти к оплате", url=send_requests)
    ).add(
        ikb("🔄 Проверить оплату", callback_data=f"Pay:{get_way}:{get_receipt}")
    )

    return keyboard


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        ikb("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}")
    ).add(
        ikb("🔙 Вернуться", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        ikb("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}"),
        ikb("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        ikb("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard
