# - *- coding: utf- 8 - *-
import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import BOT_VERSION, get_desc
from tgbot.database.db_purchases import Purchasesx
from tgbot.database.db_settings import Settingsx
from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.inline_user_page import *
from tgbot.utils.const_functions import ded, del_message, convert_date
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text, insert_tags, get_items_available
from tgbot.utils.text_functions import open_profile_user

router = Router(name=__name__)


# Открытие товаров
@router.message(F.text == "🎁 Купить")
async def user_shop(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await message.answer(
            "<b>🎁 Выберите нужный вам товар:</b>",
            reply_markup=prod_item_category_swipe_fp(0),
        )
    else:
        await message.answer("<b>🎁 Увы, товары в данное время отсутствуют.</b>")


# Открытие профиля
@router.message(F.text == "👤 Профиль")
async def user_profile(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await open_profile_user(bot, message.from_user.id)


# Проверка товаров в наличии
@router.message(F.text == "🧮 Наличие товаров")
async def user_available(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    items_available = get_items_available()

    if len(items_available) >= 1:
        await message.answer(
            items_available[0],
            reply_markup=prod_available_swipe_fp(0, len(items_available)),
        )
    else:
        await message.answer("<b>🎁 Увы, товары в данное время отсутствуют.</b>")

# Открытие FAQ
@router.message(F.text.in_(('❔ FAQ', '/faq')))
async def user_faq(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()
    send_message = get_settings.misc_faq

    if send_message == "None":
        send_message = ded(f"""
            ❔ Информация. Измените её в настройках бота.
            ➖➖➖➖➖➖➖➖➖➖
            {get_desc()}
        """)

    await message.answer(
        insert_tags(message.from_user.id, send_message),
        disable_web_page_preview=True,
    )


# Открытие сообщения с ссылкой на поддержку
@router.message(F.text.in_(('☎️ Поддержка', '/support')))
async def user_support(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()

    if get_settings.misc_support == "None":
        return await message.answer(
            ded(f"""
                ☎️ Поддержка. Измените её в настройках бота.
                ➖➖➖➖➖➖➖➖➖➖
                {get_desc()}
            """),
            disable_web_page_preview=True,
        )

    await message.answer(
        "<b>☎️ Нажмите кнопку ниже для связи с Администратором.</b>",
        reply_markup=user_support_finl(get_settings.misc_support),
    )


# Получение версии бота
@router.message(Command(commands=['version']))
async def admin_version(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(f"<b>❇️ Текущая версия бота: <code>{BOT_VERSION}</code></b>")


# Получение информации о боте
@router.message(Command(commands=['dj_desc']))
async def admin_desc(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(get_desc(), disable_web_page_preview=True)


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
