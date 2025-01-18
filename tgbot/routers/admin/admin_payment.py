# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database import Paymentsx
from tgbot.keyboards.inline_admin import payment_yoomoney_finl, close_finl, payment_cryptobot_finl, payment_cryptocloud_finl, back_to_payment_settings
from tgbot.services.api_cryptobot import CryptobotAPI
from tgbot.services.api_yoomoney import YoomoneyAPI
from tgbot.services.api_cryptocloud import CryptocloudAPI
from tgbot.utils.const_functions import ded
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


# Управление - CryptoBot
@router.callback_query(F.data == "inline_payment_cryptocloud")
async def payment_cryptobot_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.message.edit_text(
        "<b>₿ Управление - Cryptocloud</b>",
        reply_markup=payment_cryptocloud_finl(),
    )

# Управление - CryptoBot
@router.callback_query(F.data == "inline_payment_cryptobot")
async def payment_cryptobot_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.message.edit_text(
        "<b>🔷 Управление - CryptoBot</b>",
        reply_markup=payment_cryptobot_finl(),
    )


# Управление - ЮMoney
@router.callback_query(F.data == "inline_payment_yoomoney")
async def payment_yoomoney_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.message.edit_text(
        "<b>🔮 Управление - ЮMoney</b>",
        reply_markup=payment_yoomoney_finl(),
    )


##################################################################################
#################################### CRYPTOCLOUD #################################
# Баланс - CryptoBot
@router.callback_query(F.data == "payment_cryptocloud_balance")
async def payment_cryptobot_balance(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await CryptocloudAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).balance()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Информация - CryptoBot
@router.callback_query(F.data == "payment_cryptocloud_check")
async def payment_cryptocloud_check(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    status, response = await CryptocloudAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).check()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )

# Изменение - Cryptocloud
@router.callback_query(F.data == "payment_cryptocloud_edit")
async def payment_cryptobot_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.set_state("here_cryptocloud_token")
    await call.message.edit_text(
        ded(f"""
            <b>₿ Отправьте токен Cryptocloud</b>
        """)
    )

# Выключатель - Cryptocloud
@router.callback_query(F.data.startswith("payment_cryptocloud_status:"))
async def payment_cryptocloud_status(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_payments = Paymentsx.get()

    if get_status == "True" and get_payments.cryptocloud_token == "None":
        return await call.answer("❌ Токен данной платежной системы не был добавлен", True)

    Paymentsx.update(status_cryptocloud=get_status)

    await call.message.edit_text(
        "<b>₿ Управление - Cryptocloud</b>",
        reply_markup=payment_cryptocloud_finl(),
    )

############################# ПРИНЯТИЕ CRYPTOCLOUD ###############################
# Принятие токена Cryptocloud
@router.message(StateFilter("here_cryptocloud_token"))
async def payment_cryptocloud_set_token(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.update_data(cryptocloud_token=message.text)

    await state.set_state("here_cryptocloud_shop_id")
    await message.answer("<b>₿ Отправьте Shop ID Cryptocloud</b>")


@router.message(StateFilter("here_cryptocloud_shop_id"))
async def payment_cryptocloud_set_shop_id(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()
    cryptocloud_token = state_data.get("cryptocloud_token")

    await state.clear()

    await state.set_state("here_cryptocloud_shop_id")
    cache_message = await message.answer("<b>₿ Проверка введённых Cryptocloud данных... 🔄</b>")

    status, response = await CryptocloudAPI(
        bot=bot,
        arSession=arSession,
        update=message,
        skipping_error=True,
        token=cryptocloud_token,
        shop_id=message.text
    ).check()

    if status:
        Paymentsx.update(cryptocloud_token=cryptocloud_token, cryptocloud_shop_id=message.text)
        await cache_message.edit_text("<b>₿ Cryptocloud был успешно привязан ✅</b>")
    else:
        await cache_message.edit_text("<b>₿ Не удалось привязать Cryptocloud ❌</b>")

    await message.answer(
        "<b>₿ Управление - Cryptocloud</b>",
        reply_markup=payment_cryptocloud_finl(),
    )


################################################################################
################################### CRYPTOBOT ##################################
# Баланс - CryptoBot
@router.callback_query(F.data == "payment_cryptobot_balance")
async def payment_cryptobot_balance(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await CryptobotAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).balance()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Информация - CryptoBot
@router.callback_query(F.data == "payment_cryptobot_check")
async def payment_cryptobot_check(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    status, response = await CryptobotAPI(
        bot=bot,
        arSession=arSession,
        update=call,
        skipping_error=True,
    ).check()

    await call.message.answer(
        response,
        reply_markup=close_finl(),
    )


# Изменение - CryptoBot
@router.callback_query(F.data == "payment_cryptobot_edit")
async def payment_cryptobot_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.set_state("here_cryptobot_token")
    await call.message.edit_text(
        ded(f"""
            <b>🔷 Изменение @CryptoBot кошелька - <a href='https://teletype.in/@djimbox/djimboshop-cryptobot'>Инструкция</a></b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Создайте Приложение в "Crypto Pay" и отправьте токен
        """),
        disable_web_page_preview=True,
    )


# Выключатель - CryptoBot
@router.callback_query(F.data.startswith("payment_cryptobot_status:"))
async def payment_cryptobot_status(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_payments = Paymentsx.get()

    if get_status == "True" and get_payments.cryptobot_token == "None":
        return await call.answer("❌ Токен данной платежной системы не был добавлен", True)

    Paymentsx.update(status_cryptobot=get_status)

    await call.message.edit_text(
        "<b>🔷 Управление - CryptoBot</b>",
        reply_markup=payment_cryptobot_finl(),
    )


############################# ПРИНЯТИЕ CRYPTOBOT ###############################
# Принятие токена Cryptobot
@router.message(StateFilter("here_cryptobot_token"))
async def payment_cryptobot_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    get_token = message.text

    await state.clear()

    cache_message = await message.answer("<b>🔷 Проверка введённых CryptoBot данных... 🔄</b>")

    status, response = await CryptobotAPI(
        bot=bot,
        arSession=arSession,
        update=message,
        skipping_error=True,
        token=get_token
    ).check()

    if status:
        Paymentsx.update(cryptobot_token=get_token)
        await cache_message.edit_text("<b>🔷 CryptoBot кошелёк был успешно привязан ✅</b>")
    else:
        await cache_message.edit_text("<b>🔷 Не удалось привязать CryptoBot кошелёк ❌</b>")

    await message.answer(
        "<b>🔷 Управление - CryptoBot</b>",
        reply_markup=payment_cryptobot_finl(),
    )


################################################################################
#################################### ЮMoney ####################################
# Баланс - ЮMoney
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


# Информация - ЮMoney
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


# Изменение - ЮMoney
@router.callback_query(F.data == "payment_yoomoney_edit")
async def payment_yoomoney_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    response = await YoomoneyAPI(
        bot=bot,
        arSession=arSession
    ).authorization_get()

    await state.set_state("here_yoomoney_token")
    await call.message.edit_text(
        ded(f"""
            <b>🔮 Изменение ЮMoney кошелька - <a href='https://teletype.in/@djimbox/editor/djimboshop-yoomoney'>Инструкция</a></b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Отправьте ссылку/код из адресной строки
            ▪️ {response}
        """),
        disable_web_page_preview=True,
    )


# Выключатель - ЮMoney
@router.callback_query(F.data.startswith("payment_yoomoney_status:"))
async def payment_yoomoney_status(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_payments = Paymentsx.get()

    if get_status == "True" and get_payments.yoomoney_token == "None":
        return await call.answer("❌ Токен данной платежной системы не был добавлен", True)

    Paymentsx.update(status_yoomoney=get_status)

    await call.message.edit_text(
        "<b>🔮 Управление - ЮMoney</b>",
        reply_markup=payment_yoomoney_finl(),
    )


################################ ПРИНЯТИЕ ЮMONEY ###############################
# Принятие токена ЮMoney
@router.message(StateFilter("here_yoomoney_token"))
async def payment_yoomoney_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    get_code = message.text

    try:
        get_code = get_code[get_code.index("code=") + 5:].replace(" ", "")
    except:
        ...

    cache_message = await message.answer("<b>🔮 Проверка введённых ЮMoney данных... 🔄</b>")

    status, token, response = await YoomoneyAPI(
        bot=bot,
        arSession=arSession,
    ).authorization_enter(str(get_code))

    if status:
        Paymentsx.update(yoomoney_token=token)

    await cache_message.edit_text(response)

    await state.clear()
    await message.answer(
        "<b>🔮 Управление - ЮMoney</b>",
        reply_markup=payment_yoomoney_finl(),
    )
