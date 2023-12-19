# - *- coding: utf- 8 - *-
import asyncio
import json
from datetime import datetime
from typing import Union

from aiogram import Bot
from aiogram.types import FSInputFile

from tgbot.data.config import get_admins, BOT_VERSION, PATH_DATABASE, get_desc
from tgbot.database.db_category import Categoryx
from tgbot.database.db_item import Itemx
from tgbot.database.db_position import Positionx, PositionModel
from tgbot.database.db_settings import Settingsx
from tgbot.database.db_users import Userx
from tgbot.utils.const_functions import get_unix, get_date, ded, send_admins
from tgbot.utils.misc.bot_models import ARS
from tgbot.utils.text_functions import get_statistics


# Уведомление и проверка обновления при запуске бота
async def startup_notify(bot: Bot, arSession: ARS):
    if len(get_admins()) >= 1:
        await send_admins(
            bot,
            ded(f"""
                <b>✅ Бот был успешно запущен</b>
                ➖➖➖➖➖➖➖➖➖➖
                {get_desc()}
                ➖➖➖➖➖➖➖➖➖➖
                <code>❗ Данное сообщение видят только администраторы бота.</code>
            """),
        )

        await check_update(bot, arSession)


# Автоматическая очистка ежедневной статистики после 00:00:15
async def update_profit_day(bot: Bot):
    await send_admins(bot, get_statistics())

    Settingsx.update(misc_profit_day=get_unix())


# Автоматическая очистка еженедельной статистики в понедельник 00:00:10
async def update_profit_week():
    Settingsx.update(misc_profit_week=get_unix())


# Автоматическое обновление счётчика каждый месяц первого числа в 00:00:05
async def update_profit_month():
    Settingsx.update(misc_profit_month=get_unix())


# Проверка на перенесение БД из старого бота в нового или указание токена нового бота
async def check_bot_username(bot: Bot):
    get_login = Settingsx.get()
    get_bot = await bot.get_me()

    if get_bot.username != get_login.misc_bot:
        Settingsx.update(misc_bot=get_bot.username)


# Автобэкапы БД для админов
async def autobackup_admin(bot: Bot):
    for admin in get_admins():
        try:
            await bot.send_document(
                admin,
                FSInputFile(PATH_DATABASE),
                caption=f"<b>📦 #BACKUP | <code>{get_date(full=False)}</code></b>",
                disable_notification=True,
            )
        except:
            ...


# Автоматическая проверка обновления каждые 24 часа
async def check_update(bot: Bot, arSession: ARS):
    session = await arSession.get_session()

    try:
        response = await session.get("https://djimbo.dev/autoshop_update.json", ssl=False)
        response_data = json.loads((await response.read()).decode())

        if float(response_data['version']) > float(BOT_VERSION):
            await send_admins(
                bot,
                ded(f"""
                    <b>❇️ Вышло обновление: <a href='{response_data['download']}'>Скачать</a></b>
                    ➖➖➖➖➖➖➖➖➖➖
                    {response_data['text']}
                    ➖➖➖➖➖➖➖➖➖➖
                    <code>❗ Данное сообщение видят только администраторы бота.</code>
                """),
            )
    except Exception as ex:
        print(f"myError check update: {ex}")


# Расссылка админам о критических ошибках и обновлениях
async def check_mail(bot: Bot, arSession: ARS):
    session = await arSession.get_session()

    try:
        response = await session.get("https://djimbo.dev/autoshop_mail.json", ssl=False)
        response_data = json.loads((await response.read()).decode())

        if response_data['status']:
            await send_admins(
                bot,
                ded(f"""
                    {response_data['text']}
                    ➖➖➖➖➖➖➖➖➖➖
                    <code>❗ Данное сообщение видят только администраторы бота.</code>
                """),
            )
    except Exception as ex:
        print(f"myError check mail: {ex}")


# Вставка тэгов юзера в текст
def insert_tags(user_id: Union[int, str], text: str) -> str:
    get_user = Userx.get(user_id=user_id)

    if "{user_id}" in text:
        text = text.replace("{user_id}", f"<b>{get_user.user_id}</b>")
    if "{username}" in text:
        text = text.replace("{username}", f"<b>{get_user.user_login}</b>")
    if "{firstname}" in text:
        text = text.replace("{firstname}", f"<b>{get_user.user_name}</b>")

    return text


# Загрузка текста на текстовый хостинг
async def upload_text(arSession: ARS, text: str) -> str:
    session = await arSession.get_session()

    spare_pass = False
    await asyncio.sleep(0.5)

    try:
        response = await session.post(
            "http://pastie.org/pastes/create",
            data={'language': 'plaintext', 'content': text},
        )

        get_link = response.url
        if "create" in str(get_link): spare_pass = True
    except:
        spare_pass = True

    if spare_pass:
        response = await session.post(
            "https://www.friendpaste.com",
            json={'language': 'text', 'title': '', 'snippet': text},
        )

        get_link = json.loads((await response.read()).decode())['url']

    return get_link


# Загрузка изображения на хостинг телеграфа
async def upload_photo(arSession: ARS, this_photo) -> str:
    session = await arSession.get_session()

    send_data = {
        'name': 'file',
        'value': this_photo,
    }

    async with session.post("https://telegra.ph/upload", data=send_data, ssl=False) as response:
        img_src = await response.json()

    return "http://telegra.ph" + img_src[0]['src']


# Наличие товаров
def get_items_available() -> list[str]:
    get_categories = Categoryx.get_all()
    save_items = []

    for category in get_categories:
        get_positions = Positionx.gets(category_id=category.category_id)

        if len(get_positions) >= 1:
            cache_items = [f'<b>➖➖➖ {category.category_name} ➖➖➖</b>']

            for position in get_positions:
                if len(cache_items) < 30:
                    get_items = Itemx.gets(position_id=position.position_id)

                    if len(get_items) >= 1:
                        cache_items.append(
                            f"{position.position_name} | {position.position_price}₽ | В наличии {len(get_items)} шт",
                        )
                else:
                    save_items.append("\n".join(cache_items))
                    cache_items = [f'<b>➖➖➖ {category.category_name} ➖➖➖</b>']

            if len(cache_items) > 1:
                save_items.append("\n".join(cache_items))

    return save_items


# Получение позиций с товарами
def get_positions_items(category_id: Union[str, int]) -> list[PositionModel]:
    get_settings = Settingsx.get()

    get_positions = Positionx.gets(category_id=category_id)

    save_positions = []

    if get_settings.misc_item_hide == "True":
        for position in get_positions:
            get_items = Itemx.gets(position_id=position.position_id)

            if len(get_items) >= 1:
                save_positions.append(position)
    else:
        save_positions = get_positions

    return save_positions


# Автонастройка UNIX времени в БД
async def autosettings_unix():
    now_day = datetime.now().day
    now_week = datetime.now().weekday()
    now_month = datetime.now().month
    now_year = datetime.now().year

    unix_day = int(datetime.strptime(f"{now_day}.{now_month}.{now_year} 0:0:0", "%d.%m.%Y %H:%M:%S").timestamp())
    unix_week = unix_day - (now_week * 86400)
    unix_month = int(datetime.strptime(f"1.{now_month}.{now_year} 0:0:0", "%d.%m.%Y %H:%M:%S").timestamp())

    Settingsx.update(
        misc_profit_day=unix_day,
        misc_profit_week=unix_week,
        misc_profit_month=unix_month,
    )
