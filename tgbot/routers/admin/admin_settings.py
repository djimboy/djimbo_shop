# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_settings import Settingsx
from tgbot.database.db_users import Userx
from tgbot.keyboards.inline_admin import turn_open_finl, settings_open_finl
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import send_admins, insert_tags

router = Router(name=__name__)


# Изменение данных
@router.message(F.text == "🖍 Изменить данные")
async def settings_data_edit(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )


# Выключатели бота
@router.message(F.text == "🕹 Выключатели")
async def settings_turn_edit(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🕹 Включение и выключение основных функций</b>",
        reply_markup=turn_open_finl(),
    )


################################## ВЫКЛЮЧАТЕЛИ #################################
# Включение/выключение тех работ
@router.callback_query(F.data.startswith("turn_work:"))
async def settings_turn_work(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_user = Userx.get(user_id=call.from_user.id)
    Settingsx.update(status_work=get_status)

    if get_status == "True":
        send_text = "🔴 Отправил бота на технические работы."
    else:
        send_text = "🟢 Вывел бота из технических работ."

    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"{send_text}",
        not_me=get_user.user_id,
    )

    await call.message.edit_reply_markup(reply_markup=turn_open_finl())


# Включение/выключение покупок
@router.callback_query(F.data.startswith("turn_buy:"))
async def settings_turn_buy(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_user = Userx.get(user_id=call.from_user.id)
    Settingsx.update(status_buy=get_status)

    if get_status == "True":
        send_text = "🟢 Включил покупки в боте."
    else:
        send_text = "🔴 Выключил покупки в боте."

    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"{send_text}",
        not_me=get_user.user_id,
    )

    await call.message.edit_reply_markup(reply_markup=turn_open_finl())


# Включение/выключение пополнений
@router.callback_query(F.data.startswith("turn_pay:"))
async def settings_turn_pay(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_user = Userx.get(user_id=call.from_user.id)
    Settingsx.update(status_refill=get_status)

    if get_status == "True":
        send_text = "🟢 Включил пополнения в боте."
    else:
        send_text = "🔴 Выключил пополнения в боте."

    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"{send_text}",
        not_me=get_user.user_id,
    )

    await call.message.edit_reply_markup(reply_markup=turn_open_finl())


############################### ИЗМЕНЕНИЕ ДАННЫХ ###############################
# Изменение поддержки
@router.callback_query(F.data == "settings_edit_support")
async def settings_support_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_settings_support")
    await call.message.edit_text(
        "<b>☎️ Отправьте юзернейм для поддержки.</b>\n"
        "❕ Юзернейм пользователя/бота/канала/чата.",
    )


# Изменение FAQ
@router.callback_query(F.data == "settings_edit_faq")
async def settings_faq_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_settings_faq")
    await call.message.edit_text(
        "<b>❔ Введите новый текст для FAQ</b>\n"
        "❕ Вы можете использовать заготовленный синтаксис и HTML разметку:\n"
        "▶️ <code>{username}</code>  - логин пользоваля\n"
        "▶️ <code>{user_id}</code>   - айди пользователя\n"
        "▶️ <code>{firstname}</code> - имя пользователя",
    )


# Изменение отображения скрытых позиций
@router.callback_query(F.data.startswith("settings_edit_item_hide:"))
async def settings_item_hide_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    status = call.data.split(":")[1]

    Settingsx.update(misc_item_hide=status)

    await call.message.edit_text(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )


################################ ПРИНЯТИЕ ДАННЫХ ###############################
# Принятие поддержки
@router.message(F.text, StateFilter("here_settings_support"))
async def settings_support_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    get_support = message.text

    if get_support.startswith("@"):
        get_support = get_support[1:]

    await state.clear()

    Settingsx.update(misc_support=get_support)

    await message.answer(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )


# Принятие FAQ
@router.message(F.text, StateFilter("here_settings_faq"))
async def settings_faq_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    get_message = insert_tags(message.from_user.id, message.text)

    try:
        await (await message.answer(get_message)).delete()
    except:
        return await message.answer(
            "<b>❌ Ошибка синтаксиса HTML.</b>\n"
            "❔ Введите новый текст для FAQ",
        )

    await state.clear()
    Settingsx.update(misc_faq=message.text)

    await message.answer(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )
