# - *- coding: utf- 8 - *-
import asyncio
import json

from aiogram import Dispatcher
from bs4 import BeautifulSoup

from tgbot.data.config import get_admins, BOT_VERSION, BOT_DESCRIPTION
from tgbot.data.loader import bot
from tgbot.keyboards.reply_all import menu_frep
from tgbot.services.api_sqlite import get_settingsx, update_settingsx, get_userx, get_purchasesx, get_all_positionsx, \
    update_positionx, get_all_categoriesx, get_all_purchasesx, get_all_refillx, get_all_usersx, get_all_itemsx, \
    get_itemsx, get_positionx, get_categoryx
from tgbot.utils.const_functions import get_unix, convert_day


# Уведомление и проверка обновления при запуске бота
async def on_startup_notify(dp: Dispatcher, rSession):
    if len(get_admins()) >= 1:
        await send_admins(f"<b>✅ Бот был успешно запущен</b>\n"
                          f"➖➖➖➖➖➖➖➖➖➖\n"
                          f"{BOT_DESCRIPTION}\n"
                          f"➖➖➖➖➖➖➖➖➖➖\n"
                          f"<code>❗ Данное сообщение видят только администраторы бота.</code>",
                          markup="default")
        await check_update(rSession)


# Рассылка сообщения всем администраторам
async def send_admins(message, markup=None, not_me=0):
    for admin in get_admins():
        if markup == "default": markup = menu_frep(admin)

        try:
            if str(admin) != str(not_me):
                await bot.send_message(admin, message, reply_markup=markup, disable_web_page_preview=True)
        except ZeroDivisionError:
            pass


# Автоматическая очистка ежедневной статистики после 00:00
async def update_profit_day():
    await send_admins(get_statisctics())

    update_settingsx(misc_profit_day=get_unix())


# Автоматическая очистка еженедельной статистики в понедельник 00:01
async def update_profit_week():
    update_settingsx(misc_profit_week=get_unix())


# Автоматическая проверка обновления каждые 24 часа
async def check_update(rSession):
    session = await rSession.get_session()

    response = await session.get("https://sites.google.com/view/check-update-autoshop/main-page", ssl=False)
    soup_parse = BeautifulSoup(await response.read(), "html.parser")
    get_bot_update = soup_parse.select("p[class$='CDt4Ke zfr3Q']")[0].text.split("^^^")

    if float(get_bot_update[0]) > float(BOT_VERSION):
        update_description = get_bot_update[2].replace("***", "\n")

        await send_admins(f"<b>❇ Вышло обновление: <a href='{get_bot_update[1]}'>Скачать</a></b>\n"
                          f"➖➖➖➖➖➖➖➖➖➖\n"
                          f"{update_description}\n"
                          f"➖➖➖➖➖➖➖➖➖➖\n"
                          f"<code>❗ Данное сообщение видят только администраторы бота.</code>")


# Получение faq
def get_faq(user_id, send_message):
    get_user = get_userx(user_id=user_id)

    if "{user_id}" in send_message:
        send_message = send_message.replace("{user_id}", f"<b>{get_user['user_id']}</b>")
    if "{username}" in send_message:
        send_message = send_message.replace("{username}", f"<b>{get_user['user_login']}</b>")
    if "{firstname}" in send_message:
        send_message = send_message.replace("{firstname}", f"<b>{get_user['user_name']}</b>")

    return send_message


# Загрузка текста на текстовый хостинг
async def upload_text(dp, get_text):
    session = await (dp.bot['rSession']).get_session()

    spare_pass = False
    await asyncio.sleep(0.5)

    try:
        response = await session.post("http://pastie.org/pastes/create",
                                      data={"language": "plaintext", "content": get_text})

        get_link = response.url
        if "create" in str(get_link): spare_pass = True
    except:
        spare_pass = True

    if spare_pass:
        response = await session.post("https://www.friendpaste.com",
                                      json={"language": "text", "title": "", "snippet": get_text})

        get_link = json.loads((await response.read()).decode())['url']

    return get_link


# Проверка на перенесение БД из старого бота в нового или указание токена нового бота
async def check_bot_data():
    get_login = get_settingsx()['misc_bot']
    get_bot = await bot.get_me()

    if get_login not in [get_bot.username, "None"]:
        get_positions = get_all_positionsx()

        for position in get_positions:
            update_positionx(position['position_id'], position_photo="")

    update_settingsx(misc_bot=get_bot.username)


# Получить информацию о позиции для админа
def get_position_admin(position_id):
    get_items = get_itemsx(position_id=position_id)
    get_position = get_positionx(position_id=position_id)
    get_category = get_categoryx(category_id=get_position['category_id'])

    text_description = "<code>Отсутствует ❌</code>"
    photo_text = "<code>Отсутствует ❌</code>"
    get_photo = None

    if len(get_position['position_photo']) >= 5:
        photo_text = "<code>Присутствует ✅</code>"
        get_photo = get_position['position_photo']

    if get_position['position_description'] != "0":
        text_description = f"\n{get_position['position_description']}"

    get_message = f"<b>📁 Позиция: <code>{get_position['position_name']}</code></b>\n" \
                  f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                  f"🗃 Категория: <code>{get_category['category_name']}</code>\n" \
                  f"💰 Стоимость: <code>{get_position['position_price']}₽</code>\n" \
                  f"📦 Количество: <code>{len(get_items)}шт</code>\n" \
                  f"📸 Изображение: {photo_text}\n" \
                  f"📜 Описание: {text_description}"

    return get_message, get_photo


# Открытие своего профиля
def open_profile_my(user_id):
    get_purchases = get_purchasesx(user_id=user_id)
    get_user = get_userx(user_id=user_id)
    count_items = 0

    how_days = int(get_unix() - get_user['user_unix']) // 60 // 60 // 24

    if len(get_purchases) >= 1:
        for items in get_purchases:
            count_items += int(items['purchase_count'])

    return f"<b>👤 Ваш профиль:</b>\n" \
           f"➖➖➖➖➖➖➖➖➖➖\n" \
           f"🆔 ID: <code>{get_user['user_id']}</code>\n" \
           f"💰 Баланс: <code>{get_user['user_balance']}₽</code>\n" \
           f"🎁 Куплено товаров: <code>{count_items}шт</code>\n" \
           f"🕰 Регистрация: <code>{get_user['user_date'].split(' ')[0]} ({convert_day(how_days)})</code>"


# Открытие профиля при поиске
def open_profile_search(user_id):
    get_purchases = get_purchasesx(user_id=user_id)
    get_user = get_userx(user_id=user_id)
    count_items = 0

    how_days = int(get_unix() - get_user['user_unix']) // 60 // 60 // 24

    if len(get_purchases) >= 1:
        for items in get_purchases:
            count_items += items['purchase_count']

    return f"<b>👤 Профиль пользователя: <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a></b>\n" \
           f"➖➖➖➖➖➖➖➖➖➖\n" \
           f"🆔 ID: <code>{get_user['user_id']}</code>\n" \
           f"👤 Логин: <b>@{get_user['user_login']}</b>\n" \
           f"Ⓜ Имя: <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a>\n" \
           f"🕰 Регистрация: <code>{get_user['user_date']} ({convert_day(how_days)})</code>\n" \
           f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"💰 Баланс: <code>{get_user['user_balance']}₽</code>\n" \
           f"💰 Всего пополнено: <code>{get_user['user_refill']}₽</code>\n" \
           f"🎁 Куплено товаров: <code>{count_items}шт</code>"


# Статистика бота
def get_statisctics():
    show_profit_all, show_profit_day, show_profit_week = 0, 0, 0
    show_refill_all, show_refill_day, show_refill_week = 0, 0, 0
    show_users_all, show_users_day, show_users_week = 0, 0, 0
    show_money_users, show_buy_items = 0, 0

    get_categories = get_all_categoriesx()
    get_positions = get_all_positionsx()
    get_purchases = get_all_purchasesx()
    get_refill = get_all_refillx()
    get_settings = get_settingsx()
    get_items = get_all_itemsx()
    get_users = get_all_usersx()

    for purchase in get_purchases:
        show_profit_all += purchase['purchase_price']
        show_buy_items += purchase['purchase_count']

        if purchase['purchase_unix'] - get_settings['misc_profit_day'] >= 0:
            show_profit_day += purchase['purchase_price']
        if purchase['purchase_unix'] - get_settings['misc_profit_week'] >= 0:
            show_profit_week += purchase['purchase_price']

    for refill in get_refill:
        show_refill_all += refill['refill_amount']

        if refill['refill_unix'] - get_settings['misc_profit_day'] >= 0:
            show_refill_day += refill['refill_amount']
        if refill['refill_unix'] - get_settings['misc_profit_week'] >= 0:
            show_refill_week += refill['refill_amount']

    for user in get_users:
        show_money_users += user['user_balance']
        show_users_all += 1

        if user['user_unix'] - get_settings['misc_profit_day'] >= 0:
            show_users_day += 1
        if user['user_unix'] - get_settings['misc_profit_week'] >= 0:
            show_users_week += 1

    return "<b>📊 СТАТИСТИКА БОТА</b>\n" \
           f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"<b>🔶 Пользователи 🔶</b>\n" \
           f"👤 Юзеров за День: <code>{show_users_day}</code>\n" \
           f"👤 Юзеров за Неделю: <code>{show_users_week}</code>\n" \
           f"👤 Юзеров за Всё время: <code>{show_users_all}</code>\n" \
           f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"<b>🔶 Средства 🔶</b>\n" \
           f"💸 Продаж за День: <code>{show_profit_day}₽</code>\n" \
           f"💸 Продаж за Неделю: <code>{show_profit_week}₽</code>\n" \
           f"💸 Продаж за Всё время: <code>{show_profit_all}₽</code>\n" \
           f"💳 Средств в системе: <code>{show_money_users}₽</code>\n" \
           f"💰 Пополнений за День: <code>{show_refill_day}₽</code>\n" \
           f"💰 Пополнений за Неделю: <code>{show_refill_week}₽</code>\n" \
           f"💰 Пополнений за Всё время: <code>{show_refill_all}₽</code>\n" \
           f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"<b>🔶 Прочее 🔶</b>\n" \
           f"🎁 Товаров: <code>{len(get_items)}шт</code>\n" \
           f"📁 Позиций: <code>{len(get_positions)}шт</code>\n" \
           f"🗃 Категорий: <code>{len(get_categories)}шт</code>\n" \
           f"🎁 Продано товаров: <code>{show_buy_items}шт</code>\n"
