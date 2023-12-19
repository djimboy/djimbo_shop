# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_payments import Paymentsx
from tgbot.keyboards.inline_admin import payment_method_finl, payment_yoomoney_finl, close_finl, payment_qiwi_finl
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_yoomoney import YoomoneyAPI
from tgbot.utils.const_functions import ded
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


################################################################################
############################ ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ##########################
# Открытие способов пополнения
@router.message(F.text == "🖲 Способы пополнений")
async def payment_methods(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🖲 Выберите способы пополнений</b>",
        reply_markup=payment_method_finl(),
    )


# Включение/выключение самих способов пополнения
@router.callback_query(F.data.startswith("payment_method:"))
async def payment_methods_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    way_pay = call.data.split(":")[1]
    way_status = call.data.split(":")[2]

    get_payment = Paymentsx.get()

    if way_pay == "QIWI":
        if way_status == "True" and get_payment.qiwi_login == "None":
            return await call.answer("❗ Добавьте QIWI кошелёк перед включением Способов пополнений", True)

        Paymentsx.update(way_qiwi=way_status)
    elif way_pay == "Yoomoney":
        if way_status == "True" and get_payment.yoomoney_token == "None":
            return await call.answer("❗ Добавьте ЮMoney кошелёк перед включением Способов пополнений", True)

        Paymentsx.update(way_yoomoney=way_status)

    await call.message.edit_text(
        "<b>🖲 Выберите способы пополнений</b>",
        reply_markup=payment_method_finl(),
    )


# Открытие ЮMoney
@router.message(F.text == "🔮 ЮMoney")
async def payment_yoomoney_open(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🔮 Управление - ЮMoney</b>",
        reply_markup=payment_yoomoney_finl(),
    )


# Открытие QIWI
@router.message(F.text == "🥝 QIWI")
async def payment_qiwi_open(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🥝 Управление - QIWI</b>",
        reply_markup=payment_qiwi_finl(),
    )


################################################################################
#################################### ЮMoney ####################################
# Баланс ЮMoney
@router.callback_query(F.data == "payment_yoomoney_balance")
async def payment_yoomoney_balance(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await YoomoneyAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).balance()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Проверка ЮMoney
@router.callback_query(F.data == "payment_yoomoney_check")
async def payment_yoomoney_check(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await YoomoneyAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).check()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Изменение ЮMoney
@router.callback_query(F.data == "payment_yoomoney_edit")
async def payment_yoomoney_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await YoomoneyAPI(
        bot=bot,
        arSession=arSession
    ).authorization_get()

    await state.set_state("here_yoomoney_token")
    await call.message.edit_text(
        ded(f"""
            <b>🔮 Для изменения ЮMoney кошелька</b>
            ▪️ Перейдите по ссылке ниже и авторизуйте приложение.
            ▪️ После авторизации, отправьте ссылку или код из адресной строки.
            🔗 {response}
        """),
        disable_web_page_preview=True,
    )


################################ ПРИНЯТИЕ ЮMONEY ###############################
# Принятие токена ЮMoney
@router.message(StateFilter("here_yoomoney_token"))
async def payment_yoomoney_edit_token(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    cache_message = await message.answer("<b>🔮 Проверка введённых ЮMoney данных... 🔄</b>")

    get_code = message.text

    try:
        get_code = get_code[get_code.index("code=") + 5:].replace(" ", "")
    except:
        ...

    status, token, response = await YoomoneyAPI(
        bot=bot,
        arSession=arSession,
    ).authorization_enter(str(get_code))

    if status:
        Paymentsx.update(yoomoney_token=token)

    await cache_message.edit_text(response)

    await message.answer(
        "<b>🔮 Управление - ЮMoney</b>",
        reply_markup=payment_yoomoney_finl(),
    )


################################################################################
##################################### QIWI #####################################
# Баланс QIWI
@router.callback_query(F.data == "payment_qiwi_balance")
async def payment_qiwi_balance(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await QiwiAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).balance()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Проверка QIWI
@router.callback_query(F.data == "payment_qiwi_check")
async def payment_qiwi_check(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    status, response = await QiwiAPI(
        bot=bot,
        arSession=arSession,
        update=call,
    ).check()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Изменение QIWI
@router.callback_query(F.data == "payment_qiwi_edit")
async def payment_qiwi_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.set_state("here_qiwi_login")
    await call.message.edit_text(
        "<b>🥝 Введите <code>номер (через +7, +380)</code> QIWI кошелька</b>"
    )


################################ ПРИНЯТИЕ QIWI #################################
# Принятие логина для QIWI
@router.message(F.text, StateFilter("here_qiwi_login"))
async def payment_qiwi_edit_login(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if message.text.startswith("+"):
        await state.update_data(here_qiwi_login=message.text)

        await state.set_state("here_qiwi_token")
        await message.answer(
            "<b>🥝 Введите <code>токен API</code> QIWI кошелька 🖍</b>\n"
            "❕ Получить можно тут 👉 <a href='https://qiwi.com/api-info'><b>Нажми на меня</b></a>",
            disable_web_page_preview=True
        )
    else:
        await message.answer(
            "<b>❌ Номер должен начинаться с + <code>(+7..., +380...)</code></b>\n"
            "🥝 Введите <code>номер (через +7, +380)</code> QIWI кошелька 🖍",
        )


# Принятие токена для QIWI
@router.message(F.text, StateFilter("here_qiwi_token"))
async def payment_qiwi_edit_token(message: Message, bot: Bot, state: FSM, arSession: ARS):
    qiwi_login = (await state.get_data())['here_qiwi_login']
    qiwi_token = message.text

    await state.clear()

    cache_message = await message.answer("<b>🥝 Проверка введённых QIWI данных... 🔄</b>")

    status, response = await QiwiAPI(
        bot=bot,
        arSession=arSession,
        login=qiwi_login,
        token=qiwi_token,
    ).edit()

    if status:
        Paymentsx.update(
            qiwi_login=qiwi_login,
            qiwi_token=qiwi_token,
        )

    await cache_message.edit_text(response)

    await message.answer(
        "<b>🥝 Управление - QIWI</b>",
        reply_markup=payment_qiwi_finl(),
    )
