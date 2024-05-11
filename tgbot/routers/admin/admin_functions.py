# - *- coding: utf- 8 - *-
import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_purchases import Purchasesx
from tgbot.database.db_refill import Refillx
from tgbot.database.db_users import Userx
from tgbot.keyboards.inline_admin import profile_search_return_finl, mail_confirm_finl
from tgbot.utils.const_functions import is_number, to_number, del_message, ded, get_unix, clear_html, convert_date
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text
from tgbot.utils.text_functions import open_profile_admin, refill_open_admin, purchase_open_admin

router = Router(name=__name__)


# Поиск чеков и профилей
@router.message(F.text == "🔍 Поиск")
async def functions_search(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_search")
    await message.answer("<b>🔍 Отправьте айди/логин пользователя или номер чека</b>")


# Рассылка
@router.message(F.text == "📢 Рассылка")
async def functions_mail(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_mail_text")
    await message.answer(
        "<b>📢 Введите текст для рассылки пользователям</b>\n"
        "❕ Вы можете использовать HTML разметку",
    )


##################################### ПОИСК ####################################
# Принятие айди/логина пользователя или чека для поиска
@router.message(F.text, StateFilter("here_search"))
@router.message(F.text.lower().startswith(('.find', 'find')))
async def functions_search_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    find_data = message.text.lower()

    if ".find" in find_data or "find" in find_data:
        if len(find_data.split(" ")) >= 2:
            if ".find" in find_data or "find" in find_data:
                find_data = message.text.split(" ")[1]
        else:
            return await message.answer(
                "<b>❌ Вы не указали поисковые данные.</b>\n"
                "🔍 Отправьте айди/логин пользователя или номер чека",
            )

    if find_data.startswith("@") or find_data.startswith("#"):
        find_data = find_data[1:]

    if find_data.isdigit():
        get_user = Userx.get(user_id=find_data)
    else:
        get_user = Userx.get(user_login=find_data.lower())

    get_refill = Refillx.get(refill_receipt=find_data)
    get_purchase = Purchasesx.get(purchase_receipt=find_data)

    if get_user is None and get_refill is None and get_purchase is None:
        return await message.answer(
            "<b>❌ Данные не были найдены</b>\n"
            "🔍 Отправьте айди/логин пользователя или номер чека",
        )

    await state.clear()

    if get_user is not None:
        return await open_profile_admin(bot, message.from_user.id, get_user)

    if get_refill is not None:
        return await refill_open_admin(bot, message.from_user.id, get_refill)

    if get_purchase is not None:
        return await purchase_open_admin(bot, arSession, message.from_user.id, get_purchase)


################################### РАССЫЛКА ###################################
# Принятие текста для рассылки
@router.message(F.text, StateFilter("here_mail_text"))
async def functions_mail_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.update_data(here_mail_text="📢 Рассылка.\n" + str(message.text))

    get_users = Userx.get_all()

    try:
        await (await message.answer(message.text)).delete()
    except:
        return await message.answer(
            "<b>❌ Ошибка синтаксиса HTML.</b>\n"
            "📢 Введите текст для рассылки пользователям.\n"
            "❕ Вы можете использовать HTML разметку.",
        )

    await state.set_state("here_mail_confirm")

    await message.answer(
        f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам сообщение?</b>\n"
        f"{message.text}",
        reply_markup=mail_confirm_finl(),
        disable_web_page_preview=True
    )


# Подтверждение отправки рассылки
@router.callback_query(F.data.startswith("confirm_mail:"), StateFilter("here_mail_confirm"))
async def functions_mail_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_action = call.data.split(":")[1]

    get_users = Userx.get_all()

    send_message = (await state.get_data())['here_mail_text']
    await state.clear()

    if get_action == "yes":
        await call.message.edit_text(f"<b>📢 Рассылка началась... (0/{len(get_users)})</b>")

        await asyncio.create_task(functions_mail_make(bot, send_message, call))
    else:
        await call.message.edit_text("<b>📢 Вы отменили отправку рассылки ✅</b>")


# Сама отправка рассылки
async def functions_mail_make(bot: Bot, text: str, call: CallbackQuery):
    users_receive, users_block, users_count = 0, 0, 0

    get_users = Userx.get_all()
    get_time = get_unix()

    for user in get_users:
        try:
            await bot.send_message(user.user_id, text)
            users_receive += 1
        except:
            users_block += 1

        users_count += 1

        if users_count % 10 == 0:
            await call.message.edit_text(f"<b>📢 Рассылка началась... ({users_count}/{len(get_users)})</b>")

        await asyncio.sleep(0.07)

    await call.message.edit_text(
        ded(f"""
            <b>📢 Рассылка была завершена за <code>{get_unix() - get_time}сек</code></b>
            ➖➖➖➖➖➖➖➖➖➖
            👤 Всего пользователей: <code>{len(get_users)}</code>
            ✅ Пользователей получило сообщение: <code>{users_receive}</code>
            ❌ Пользователей не получило сообщение: <code>{users_block}</code>
        """)
    )


############################## УПРАВЛЕНИЕ ПРОФИЛЕМ #############################
# Обновление профиля пользователя
@router.callback_query(F.data.startswith("admin_user_refresh:"))
async def functions_profile_refresh(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    get_user = Userx.get(user_id=user_id)

    await state.clear()

    await del_message(call.message)
    await open_profile_admin(bot, call.from_user.id, get_user)


# Покупки пользователя
@router.callback_query(F.data.startswith("admin_user_purchases:"))
async def functions_profile_purchases(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    get_user = Userx.get(user_id=user_id)
    get_purchases = Purchasesx.gets(user_id=call.from_user.id)
    get_purchases = get_purchases[-10:]

    if len(get_purchases) < 1:
        return await call.answer("❗ У пользователя отсутствуют покупки", True)

    await call.answer("🎁 Последние 10 покупок")
    await del_message(call.message)

    for purchase in get_purchases:
        link_items = await upload_text(arSession, purchase.purchase_data)

        await call.message.answer(
            ded(f"""
                <b>🧾 Чек: <code>#{purchase.purchase_receipt}</code></b>
                🎁 Товар: <code>{purchase.purchase_position_name} | {purchase.purchase_count}шт | {purchase.purchase_price}₽</code>
                🕰 Дата покупки: <code>{convert_date(purchase.purchase_unix)}</code>
                🔗 Товары: <a href='{link_items}'>кликабельно</a>
            """)
        )

        await asyncio.sleep(0.2)

    await open_profile_admin(bot, call.from_user.id, get_user)


# Выдача баланса пользователю
@router.callback_query(F.data.startswith("admin_user_balance_add:"))
async def functions_profile_balance_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_add")

    await call.message.edit_text(
        "<b>💰 Введите сумму для выдачи баланса</b>",
        reply_markup=profile_search_return_finl(user_id),
    )


# Принятие суммы для выдачи баланса пользователю
@router.message(F.text, StateFilter("here_profile_add"))
async def functions_profile_balance_add_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    user_id = (await state.get_data())['here_profile']

    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно.</b>\n"
            "💰 Введите сумму для выдачи баланса",
            reply_markup=profile_search_return_finl(user_id),
        )

    get_amount = to_number(message.text)

    if get_amount <= 0 or get_amount > 1_000_000_000:
        return await message.answer(
            "<b>❌ Сумма выдачи не может быть меньше 1 и больше 1 000 000 000</b>\n"
            "💰 Введите сумму для выдачи баланса",
            reply_markup=profile_search_return_finl(user_id),
        )

    await state.clear()

    get_user = Userx.get(user_id=user_id)
    Userx.update(
        user_id,
        user_balance=round(get_user.user_balance + get_amount, 2),
        user_give=round(get_user.user_give + get_amount, 2),
    )

    try:
        await bot.send_message(
            user_id,
            f"<b>💰 Вам было выдано <code>{message.text}₽</code></b>",
        )
    except:
        ...

    await message.answer(
        f"👤 Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"💰 Выдача баланса. <code>{message.text}₽</code> -> <code>{round(get_user.user_give + get_amount, 2)}₽</code>"
    )

    get_user = Userx.get(user_id=user_id)
    await open_profile_admin(bot, message.from_user.id, get_user)


# Изменение баланса пользователю
@router.callback_query(F.data.startswith("admin_user_balance_set:"))
async def functions_profile_balance_set(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_set")

    await call.message.edit_text(
        "<b>💰 Введите сумму для изменения баланса</b>",
        reply_markup=profile_search_return_finl(user_id),
    )


# Принятие суммы для изменения баланса пользователя
@router.message(F.text, StateFilter("here_profile_set"))
async def functions_profile_balance_set_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    user_id = (await state.get_data())['here_profile']

    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно.</b>\n"
            "💰 Введите сумму для изменения баланса",
            reply_markup=profile_search_return_finl(user_id),
        )

    get_amount = to_number(message.text)

    if get_amount < -1_000_000_000 or get_amount > 1_000_000_000:
        return await message.answer(
            "<b>❌ Сумма изменения не может быть больше или меньше (-)1 000 000 000</b>\n"
            "💰 Введите сумму для изменения баланса",
            reply_markup=profile_search_return_finl(user_id),
        )

    await state.clear()

    get_user = Userx.get(user_id=user_id)

    if get_amount > get_user.user_balance:
        user_give = get_user.user_give + get_amount
    else:
        user_give = get_user.user_give

    Userx.update(
        user_id,
        user_balance=get_amount,
        user_give=user_give,
    )

    await message.answer(
        f"👤 Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"💰 Выдача баланса. <code>{message.text}₽</code> -> <code>{get_amount}₽</code>"
    )

    get_user = Userx.get(user_id=user_id)
    await open_profile_admin(bot, message.from_user.id, get_user)


# Отправка сообщения пользователю
@router.callback_query(F.data.startswith("admin_user_message:"))
async def functions_profile_user_message(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    user_id = int(call.data.split(":")[1])

    await state.update_data(here_profile=user_id)
    await state.set_state("here_profile_message")

    await call.message.edit_text(
        "<b>💌 Введите сообщение для отправки</b>\n"
        "⚠️ Сообщение будет сразу отправлено пользователю.",
        reply_markup=profile_search_return_finl(user_id),
    )


# Принятие сообщения для отправки пользователю
@router.message(F.text, StateFilter("here_profile_message"))
async def functions_profile_user_message_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    user_id = (await state.get_data())['here_profile']
    await state.clear()

    get_message = "<b>💌 Сообщение от администратора:</b>\n" + f"<code>{clear_html(message.text)}</code>"
    get_user = Userx.get(user_id=user_id)

    try:
        await bot.send_message(user_id, get_message)
    except:
        await message.answer(
            f"👤 Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
            f"❌ Не удалось отправить сообщение. Возможно пользователь заблокировал бота."
        )
    else:
        await message.answer(
            f"👤 Пользователь: <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
            f"💌 Отправлено сообщение: {get_message}"
        )

    await open_profile_admin(bot, message.from_user.id, get_user)
