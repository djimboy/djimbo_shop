# - *- coding: utf- 8 - *-
from datetime import datetime
from typing import Union

import pytz
from aiogram import Bot
from aiogram.types import LinkPreviewOptions, CallbackQuery
from aiogram.utils.markdown import hide_link

from tgbot.data.config import BOT_TIMEZONE
from tgbot.database import (Categoryx, Positionx, Itemx, Purchasesx, PurchasesModel, Refillx, RefillModel, Settingsx,
                            Userx, UserModel)
from tgbot.keyboards.inline_admin import profile_edit_finl
from tgbot.keyboards.inline_admin_products import position_edit_open_finl, category_edit_open_finl, item_delete_finl
from tgbot.keyboards.inline_user import user_profile_finl
from tgbot.keyboards.inline_user_products import products_open_finl
from tgbot.utils.const_functions import ded, get_unix, convert_day, convert_date
from tgbot.utils.misc.bot_models import ARS


################################################################################
################################# ПОЛЬЗОВАТЕЛЬ #################################
# Открытие профиля пользователем
async def open_profile_user(call: CallbackQuery, user_id: Union[int, str]):
    get_purchases = Purchasesx.gets(user_id=user_id)
    get_user = Userx.get(user_id=user_id)

    how_days = int(get_unix() - get_user.user_unix) // 60 // 60 // 24
    count_items = sum([purchase.purchase_count for purchase in get_purchases])

    send_text = ded(f"""
        <b>👤 Ваш профиль</b>
        ➖➖➖➖➖➖➖➖➖➖
        🆔 ID: <code>{get_user.user_id}</code>
        💰 Баланс: <code>{get_user.user_balance}₽</code>
        🎁 Куплено товаров: <code>{count_items}шт</code>

        🕰 Регистрация: <code>{convert_date(get_user.user_unix, False, False)} ({convert_day(how_days)})</code>
    """)

    await call.message.edit_text(
        text=send_text,
        reply_markup=user_profile_finl(),
    )


# Открытие позиции пользователем
async def position_open_user(bot: Bot, user_id: int, position_id: Union[str, int], remover: Union[str, int]):
    get_items = Itemx.gets(position_id=position_id)
    get_position = Positionx.get(position_id=position_id)
    get_category = Categoryx.get(category_id=get_position.category_id)

    if get_position.position_desc != "None":
        text_desc = f"▪️ Описание: {get_position.position_desc}"
    else:
        text_desc = ""

    send_text = ded(f"""
        <b>🎁 Покупка товара</b>{hide_link(get_position.position_photo)}
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Название: <code>{get_position.position_name}</code>
        ▪️ Категория: <code>{get_category.category_name}</code>
        ▪️ Стоимость: <code>{get_position.position_price}₽</code>
        ▪️ Количество: <code>{len(get_items)}шт</code>
        {text_desc}
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
        link_preview_options=LinkPreviewOptions(
            show_above_text=True,
        ),
        reply_markup=products_open_finl(position_id, get_position.category_id, remover),

    )


################################################################################
#################################### АДМИН #####################################
# Открытие профиля админом
async def open_profile_admin(bot: Bot, user_id: int, get_user: UserModel):
    get_purchases = Purchasesx.gets(user_id=get_user.user_id)

    how_days = int(get_unix() - get_user.user_unix) // 60 // 60 // 24
    count_items = sum([purchase.purchase_count for purchase in get_purchases])

    send_text = ded(f"""
        <b>👤 Профиль пользователя: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a></b>
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ ID: <code>{get_user.user_id}</code>
        ▪️ Логин: <b>@{get_user.user_login}</b>
        ▪️ Имя: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>
        ▪️ Регистрация: <code>{convert_date(get_user.user_unix, False, False)} ({convert_day(how_days)})</code>

        ▪️ Баланс: <code>{get_user.user_balance}₽</code>
        ▪️ Всего выдано: <code>{get_user.user_give}₽</code>
        ▪️ Всего пополнено: <code>{get_user.user_refill}₽</code>
        ▪️ Куплено товаров: <code>{count_items}шт</code>
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
        reply_markup=profile_edit_finl(get_user.user_id),
    )


# Открытие пополнения админом
async def refill_open_admin(bot: Bot, user_id: int, get_refill: RefillModel):
    get_user = Userx.get(user_id=get_refill.user_id)

    if get_refill.refill_method in ['Form', 'Nickname', 'Number', 'QIWI']:
        pay_method = "QIWI 🥝"
    elif get_refill.refill_method == "Yoomoney":
        pay_method = "ЮMoney 🔮"
    elif get_refill.refill_method == "Cryptobot":
        pay_method = "CryptoBot 🔷"
    else:
        pay_method = f"{get_refill.refill_method}"

    send_text = ded(f"""
        <b>🧾 Чек: <code>#{get_refill.refill_receipt}</code></b>
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a> | <code>{get_user.user_id}</code>
        ▪️ Сумма пополнения: <code>{get_refill.refill_amount}₽</code>
        ▪️ Способ пополнения: <code>{pay_method}</code>
        ▪️ Комментарий: <code>{get_refill.refill_comment}</code>
        ▪️ Дата пополнения: <code>{convert_date(get_refill.refill_unix)}</code>
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
    )


# Открытие покупки админом
async def purchase_open_admin(bot: Bot, arSession: ARS, user_id: int, get_purchase: PurchasesModel):
    from tgbot.utils.misc_functions import upload_text

    get_user = Userx.get(user_id=get_purchase.user_id)

    link_items = await upload_text(arSession, get_purchase.purchase_data)

    send_text = ded(f"""
        <b>🧾 Чек: <code>#{get_purchase.purchase_receipt}</code></b>
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a> | <code>{get_user.user_id}</code>

        ▪️ Название товара: <code>{get_purchase.purchase_position_name}</code>
        ▪️ Куплено товаров: <code>{get_purchase.purchase_count}шт</code>
        ▪️ Цена одного товара: <code>{get_purchase.purchase_price_one}₽</code>
        ▪️ Сумма покупки: <code>{get_purchase.purchase_price}₽</code>

        ▪️ Баланс до покупки: <code>{get_purchase.user_balance_before}₽</code>
        ▪️ Баланс после покупки: <code>{get_purchase.user_balance_after}₽</code>

        ▪️ Товары: <a href='{link_items}'>кликабельно</a>
        ▪️ Дата покупки: <code>{convert_date(get_purchase.purchase_unix)}</code>
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
    )


# Открытие категории админом
async def category_open_admin(bot: Bot, user_id: int, category_id: Union[str, int], remover: int):
    profit_amount_all, profit_amount_day, profit_amount_week, profit_amount_month = 0, 0, 0, 0
    profit_count_all, profit_count_day, profit_count_week, profit_count_month = 0, 0, 0, 0

    get_items = Itemx.gets(category_id=category_id)
    get_category = Categoryx.get(category_id=category_id)
    get_positions = Positionx.gets(category_id=category_id)

    get_purchases = Purchasesx.gets(purchase_category_id=category_id)
    get_settings = Settingsx.get()

    for purchase in get_purchases:
        profit_amount_all += purchase.purchase_price
        profit_count_all += purchase.purchase_count

        if purchase.purchase_unix - get_settings.misc_profit_day >= 0:
            profit_amount_day += purchase.purchase_price
            profit_count_day += purchase.purchase_count
        if purchase.purchase_unix - get_settings.misc_profit_week >= 0:
            profit_amount_week += purchase.purchase_price
            profit_count_week += purchase.purchase_count
        if purchase.purchase_unix - get_settings.misc_profit_month >= 0:
            profit_amount_month += purchase.purchase_price
            profit_count_month += purchase.purchase_count

    send_text = ded(f"""
        <b>🗃️ Редактирование категории</b>
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Категория: <code>{get_category.category_name}</code>
        ▪️ Кол-во позиций: <code>{len(get_positions)}шт</code>
        ▪️ Кол-во товаров: <code>{len(get_items)}шт</code>
        ▪️ Дата создания: <code>{convert_date(get_category.category_unix)}шт</code>
        
        💸 Продаж за День: <code>{profit_count_day}шт</code> - <code>{profit_amount_day}₽</code>
        💸 Продаж за Неделю: <code>{profit_count_week}шт</code> - <code>{profit_amount_week}₽</code>
        💸 Продаж за Месяц: <code>{profit_count_month}шт</code> - <code>{profit_amount_month}₽</code>
        💸 Продаж за Всё время: <code>{profit_count_all}шт</code> - <code>{profit_amount_all}₽</code>
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
        reply_markup=await category_edit_open_finl(bot, category_id, remover),
    )


# Открытие позиции админом
async def position_open_admin(bot: Bot, user_id: int, position_id: Union[str, int]):
    profit_amount_all, profit_amount_day, profit_amount_week, profit_amount_month = 0, 0, 0, 0
    profit_count_all, profit_count_day, profit_count_week, profit_count_month = 0, 0, 0, 0

    get_items = Itemx.gets(position_id=position_id)
    get_position = Positionx.get(position_id=position_id)
    get_category = Categoryx.get(category_id=get_position.category_id)

    get_purchases = Purchasesx.gets(purchase_position_id=position_id)
    get_settings = Settingsx.get()

    if get_position.position_photo != "None":
        position_photo_text = "<code>Присутствует ✅</code>"
    else:
        position_photo_text = "<code>Отсутствует ❌</code>"

    if get_position.position_desc != "None":
        position_desc = f"{get_position.position_desc}"
    else:
        position_desc = "<code>Отсутствует ❌</code>"

    for purchase in get_purchases:
        profit_amount_all += purchase.purchase_price
        profit_count_all += purchase.purchase_count

        if purchase.purchase_unix - get_settings.misc_profit_day >= 0:
            profit_amount_day += purchase.purchase_price
            profit_count_day += purchase.purchase_count
        if purchase.purchase_unix - get_settings.misc_profit_week >= 0:
            profit_amount_week += purchase.purchase_price
            profit_count_week += purchase.purchase_count
        if purchase.purchase_unix - get_settings.misc_profit_month >= 0:
            profit_amount_month += purchase.purchase_price
            profit_count_month += purchase.purchase_count

    send_text = ded(f"""
        <b>📁 Редактирование позиции</b>{hide_link(get_position.position_photo)}
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Категория: <code>{get_category.category_name}</code>
        ▪️ Позиция: <code>{get_position.position_name}</code>
        ▪️ Стоимость: <code>{get_position.position_price}₽</code>
        ▪️ Количество: <code>{len(get_items)}шт</code>
        ▪️ Изображение: {position_photo_text}
        ▪️ Дата создания: <code>{convert_date(get_category.category_unix)}</code>
        ▪️ Описание: {position_desc}

        💸 Продаж за День: <code>{profit_count_day}шт</code> - <code>{profit_amount_day}₽</code>
        💸 Продаж за Неделю: <code>{profit_count_week}шт</code> - <code>{profit_amount_week}₽</code>
        💸 Продаж за Месяц: <code>{profit_count_month}шт</code> - <code>{profit_amount_month}₽</code>
        💸 Продаж за Всё время: <code>{profit_count_all}шт</code> - <code>{profit_amount_all}₽</code>
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
        link_preview_options=LinkPreviewOptions(
            show_above_text=True,
        ),
        reply_markup=await position_edit_open_finl(bot, position_id, get_position.category_id, 0),

    )


# Открытие товара админом
async def item_open_admin(bot: Bot, user_id: int, item_id: Union[str, int], remover: int):
    get_item = Itemx.get(item_id=item_id)

    get_position = Positionx.get(position_id=get_item.position_id)
    get_category = Categoryx.get(category_id=get_item.category_id)

    send_text = ded(f"""
        <b>🎁️ Редактирование товара</b>
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Категория: <code>{get_category.category_name}</code>
        ▪️ Позиция: <code>{get_position.position_name}</code>
        ▪️ Дата добавления: <code>{convert_date(get_item.item_unix)}</code>
        ▪️ Товар: <code>{get_item.item_data}</code>
    """)

    await bot.send_message(
        chat_id=user_id,
        text=send_text,
        reply_markup=item_delete_finl(get_item.item_id, get_item.position_id, get_item.category_id),
    )


################################################################################
################################################################################
# Статистика бота
def get_statistics() -> str:
    refill_amount_all, refill_amount_day, refill_amount_week, refill_amount_month = 0, 0, 0, 0
    refill_count_all, refill_count_day, refill_count_week, refill_count_month = 0, 0, 0, 0
    profit_amount_all, profit_amount_day, profit_amount_week, profit_amount_month = 0, 0, 0, 0
    profit_count_all, profit_count_day, profit_count_week, profit_count_month = 0, 0, 0, 0
    users_all, users_day, users_week, users_month, users_money_have, users_money_give = 0, 0, 0, 0, 0, 0
    refill_cryptobot_count, refill_cryptobot_amount, refill_yoomoney_count, refill_yoomoney_amount = 0, 0, 0, 0

    get_categories = Categoryx.get_all()
    get_positions = Positionx.get_all()
    get_purchases = Purchasesx.get_all()
    get_refill = Refillx.get_all()
    get_items = Itemx.get_all()
    get_users = Userx.get_all()
    get_settings = Settingsx.get()

    # Покупки
    for purchase in get_purchases:
        profit_amount_all += purchase.purchase_price
        profit_count_all += purchase.purchase_count

        if purchase.purchase_unix - get_settings.misc_profit_day >= 0:
            profit_amount_day += purchase.purchase_price
            profit_count_day += purchase.purchase_count
        if purchase.purchase_unix - get_settings.misc_profit_week >= 0:
            profit_amount_week += purchase.purchase_price
            profit_count_week += purchase.purchase_count
        if purchase.purchase_unix - get_settings.misc_profit_month >= 0:
            profit_amount_month += purchase.purchase_price
            profit_count_month += purchase.purchase_count

    # Пополнения
    for refill in get_refill:
        refill_amount_all += refill.refill_amount
        refill_count_all += 1

        if refill.refill_method == "Yoomoney":
            refill_yoomoney_count += 1
            refill_yoomoney_amount += refill.refill_amount
        elif refill.refill_method == "Cryptobot":
            refill_cryptobot_count += 1
            refill_cryptobot_amount += refill.refill_amount

        if refill.refill_unix - get_settings.misc_profit_day >= 0:
            refill_amount_day += refill.refill_amount
            refill_count_day += 1
        if refill.refill_unix - get_settings.misc_profit_week >= 0:
            refill_amount_week += refill.refill_amount
            refill_count_week += 1
        if refill.refill_unix - get_settings.misc_profit_month >= 0:
            refill_amount_month += refill.refill_amount
            refill_count_month += 1

    # Пользователи и средства
    for user in get_users:
        users_money_have += user.user_balance
        users_money_give += user.user_give
        users_all += 1

        if user.user_unix - get_settings.misc_profit_day >= 0:
            users_day += 1
        if user.user_unix - get_settings.misc_profit_week >= 0:
            users_week += 1
        if user.user_unix - get_settings.misc_profit_month >= 0:
            users_month += 1

    # Даты обновления статистики
    all_days = [
        'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье',
    ]

    all_months = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
        'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    now_day = datetime.now().day
    now_week = datetime.now().weekday()
    now_month = datetime.now().month
    now_year = datetime.now().year

    unix_day = int(datetime.strptime(f"{now_day}.{now_month}.{now_year} 0:0:0", "%d.%m.%Y %H:%M:%S").timestamp())
    unix_week = unix_day - (now_week * 86400)

    week_day = int(datetime.fromtimestamp(unix_week, pytz.timezone(BOT_TIMEZONE)).strftime("%d"))
    week_month = int(datetime.fromtimestamp(unix_week, pytz.timezone(BOT_TIMEZONE)).strftime("%m"))
    week_week = int(datetime.fromtimestamp(unix_week, pytz.timezone(BOT_TIMEZONE)).weekday())

    return ded(f"""
        <b>📊 СТАТИСТИКА БОТА</b>
        ➖➖➖➖➖➖➖➖➖➖
        <b>👤 Пользователи</b>
        ┣ Юзеров за День: <code>{users_day}</code>
        ┣ Юзеров за Неделю: <code>{users_week}</code>
        ┣ Юзеров за Месяц: <code>{users_month}</code>
        ┗ Юзеров за Всё время: <code>{users_all}</code>

        <b>💰 Средства</b>
        ┣‒ Продажи (кол-во, сумма)
        ┣ За День: <code>{profit_count_day}шт</code> - <code>{profit_amount_day}₽</code>
        ┣ За Неделю: <code>{profit_count_week}шт</code> - <code>{profit_amount_week}₽</code>
        ┣ За Месяц: <code>{profit_count_month}шт</code> - <code>{profit_amount_month}₽</code>
        ┣ За Всё время: <code>{profit_count_all}шт</code> - <code>{profit_amount_all}₽</code>
        ┃
        ┣‒ Пополнения (кол-во, сумма)
        ┣ За День: <code>{refill_count_day}шт</code> - <code>{refill_amount_day}₽</code>
        ┣ За Неделю: <code>{refill_count_week}шт</code> - <code>{refill_amount_week}₽</code>
        ┣ За Месяц: <code>{refill_count_month}шт</code> - <code>{refill_amount_month}₽</code>
        ┣ За Всё время: <code>{refill_count_all}шт</code> - <code>{refill_amount_all}₽</code>
        ┃
        ┣‒ Платежные системы (всего)
        ┣ ЮMoney: <code>{refill_yoomoney_count}шт</code> - <code>{refill_yoomoney_amount}₽</code>
        ┣ CryptoBot: <code>{refill_cryptobot_count}шт</code> - <code>{refill_cryptobot_amount}₽</code>
        ┃
        ┣‒ Остальные
        ┣ Средств выдано: <code>{users_money_give}₽</code>
        ┗ Средств в системе: <code>{users_money_have}₽</code>

        <b>🎁 Товары</b>
        ┣ Товаров: <code>{len(get_items)}шт</code>
        ┣ Позиций: <code>{len(get_positions)}шт</code>
        ┗ Категорий: <code>{len(get_categories)}шт</code>

        <b>🕰 Даты статистики</b>
        ┣ Дневная: <code>{now_day} {all_months[now_month - 1].title()}</code>
        ┣ Недельная: <code>{week_day} {all_months[week_month - 1].title()}, {all_days[week_week]}</code>
        ┗ Месячная: <code>1 {all_months[now_month - 1].title()}, {now_year}г</code>
   """)
