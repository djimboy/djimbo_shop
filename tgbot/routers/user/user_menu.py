# - *- coding: utf- 8 - *-
import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import BOT_VERSION, get_desc
from tgbot.database import Purchasesx, Settingsx
from tgbot.keyboards.inline_user import user_support_finl, back_to_main_menu_keyboard
from tgbot.keyboards.inline_user_page import *
from tgbot.utils.const_functions import ded, del_message, convert_date
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text, insert_tags, get_items_available
from tgbot.utils.text_functions import open_profile_user

router = Router(name=__name__)


# Открытие товаров
@router.callback_query(F.data == "inline_buy")
async def user_shop(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = get_categories_items()

    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>🎁 Выберите нужную вам категорию</b>",
            reply_markup=prod_item_category_swipe_fp(0),
        )
    else:
        await call.answer(
            "Нет доступных категорий",
            True
        )


# Открытие профиля
@router.callback_query(F.data == "inline_profile")
async def user_profile(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await open_profile_user(call, call.from_user.id)


# Проверка товаров в наличии
@router.callback_query(F.data == "inline_product_availability")
async def user_available(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    items_available = get_items_available()

    if len(items_available) >= 1:
        await call.message.edit_text(
            items_available[0],
            reply_markup=prod_available_swipe_fp(0, len(items_available)),
        )
    else:
        await call.answer("🎁 Увы, товары в данное время отсутствуют", True)


# Открытие FAQ
@router.callback_query(F.data == "inline_faq")
async def user_faq(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()

    if get_settings.misc_faq == "None":
        return await call.answer(
            ded(f"""
                ❔ Текст FAQ не указан. Измените его в настройках бота.
            """),
            True
        )

    await call.message.edit_text(
        insert_tags(call.from_user.id, get_settings.misc_faq),
        disable_web_page_preview=True,
        reply_markup=back_to_main_menu_keyboard()
    )


# Открытие сообщения с ссылкой на поддержку
@router.callback_query(F.data == "inline_support")
async def user_support(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()

    if get_settings.misc_support == "None":
        return await call.answer(
            ded(f"""
                ☎️ Контакты поддержки не указаны. Измените их в настройках бота.
            """),
            True
        )

    await call.message.edit_text(
        "<b>☎️ Нажмите кнопку ниже для связи с Администратором</b>",
        reply_markup=user_support_finl(get_settings.misc_support),
    )


################################################################################
# Возвращение к профилю
@router.callback_query(F.data == "user_profile")
async def user_profile_return(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await del_message(call.message)
    await open_profile_user(bot, call.from_user.id)


# Просмотр истории покупок
@router.callback_query(F.data == "user_purchases")
async def user_purchases(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_purchases = Purchasesx.gets(user_id=call.from_user.id)
    get_purchases = get_purchases[-5:]

    if len(get_purchases) >= 1:
        await call.answer("🎁 Последние 5 покупок")
        await del_message(call.message)

        for purchase in get_purchases:
            link_items = await upload_text(arSession, purchase.purchase_data)

            await call.message.answer(
                ded(f"""
                    <b>🧾 Чек: <code>#{purchase.purchase_receipt}</code></b>
                    ▪️ Товар: <code>{purchase.purchase_position_name} | {purchase.purchase_count}шт | {purchase.purchase_price}₽</code>
                    ▪️ Дата покупки: <code>{convert_date(purchase.purchase_unix)}</code>
                    ▪️ Товары: <a href='{link_items}'>кликабельно</a>
                """)
            )

            await asyncio.sleep(0.2)

        await open_profile_user(bot, call.from_user.id)
    else:
        await call.answer("❗ У вас отсутствуют покупки", True)


# Страницы наличия товаров
@router.callback_query(F.data.startswith("user_available_swipe:"))
async def user_available_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    items_available = get_items_available()

    if remover >= len(items_available):
        remover = len(items_available) - 1
    if remover < 0:
        remover = 0

    await call.message.edit_text(
        items_available[remover],
        reply_markup=prod_available_swipe_fp(remover, len(items_available)),
    )
