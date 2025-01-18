# - *- coding: utf- 8 - *-
from typing import Union

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database import Paymentsx, Refillx, Userx
from tgbot.keyboards.inline_user import refill_bill_finl, refill_method_finl
from tgbot.services.api_cryptobot import CryptobotAPI
from tgbot.services.api_yoomoney import YoomoneyAPI
from tgbot.services.api_cryptocloud import CryptocloudAPI
from tgbot.utils.const_functions import is_number, to_number, gen_id, ded
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import send_admins

min_refill_rub = 10  # Минимальная сумма пополнения в рублях

router = Router(name=__name__)


# Выбор способа пополнения
@router.callback_query(F.data == "user_refill")
async def refill_method(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_payment = Paymentsx.get()

    if get_payment.status_cryptobot == "False" and get_payment.status_yoomoney == "False" and get_payment.status_cryptocloud == "False":
        return await call.answer("❗️ Пополнения временно недоступны", True)

    await call.message.edit_text(
        "<b>💰 Выберите способ пополнения баланса</b>",
        reply_markup=refill_method_finl(),
    )


# Выбор способа пополнения
@router.callback_query(F.data.startswith("user_refill_method:"))
async def refill_method_select(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_method = call.data.split(":")[1]

    await state.update_data(here_refill_method=pay_method)

    await state.set_state("here_refill_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")


################################################################################
################################### ВВОД СУММЫ #################################
# Принятие суммы для пополнения средств
@router.message(F.text, StateFilter("here_refill_amount"))
async def refill_amount_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer(
            ded(f"""
                <b>❌ Данные были введены неверно</b>
                💰 Введите сумму для пополнения средств
            """),
        )

    if to_number(message.text) < min_refill_rub or to_number(message.text) > 150_000:
        return await message.answer(
            ded(f"""
                <b>❌ Неверная сумма пополнения</b>
                ❗️ Cумма не должна быть меньше <code>{min_refill_rub}₽</code> и больше <code>150 000₽</code>
                💰 Введите сумму для пополнения средств
            """),
        )

    cache_message = await message.answer("<b>♻️ Подождите, платёж генерируется..</b>")

    pay_amount = to_number(message.text)
    pay_method = (await state.get_data())['here_refill_method']
    await state.clear()

    # Генерация платежа
    if pay_method == "Cryptobot":
        bill_message, bill_link, bill_receipt = await (
            CryptobotAPI(
                bot=bot,
                arSession=arSession,
                update=cache_message,
            )
        ).bill(pay_amount)
    elif pay_method == "Yoomoney":
        bill_message, bill_link, bill_receipt = await (
            YoomoneyAPI(
                bot=bot,
                arSession=arSession,
                update=cache_message
            )
        ).bill(pay_amount)
    elif pay_method == "Cryptocloud":
        bill_message, bill_link, bill_receipt = await (
            CryptocloudAPI(
                bot=bot,
                arSession=arSession,
                update=cache_message
            )
        ).bill(pay_amount)

    # Обработка статуса генерации платежа
    if bill_message:
        await cache_message.edit_text(
            bill_message,
            reply_markup=refill_bill_finl(bill_link, bill_receipt, pay_method),
        )
    else:
        await cache_message.edit_text(
            f"<b>❌ Не удалось сгенерировать платёж. Попробуйте позже</b>"
        )


################################################################################
############################### ПРОВЕРКА ПЛАТЕЖЕЙ ##############################
# Проверка оплаты - ЮMoney
@router.callback_query(F.data.startswith('Pay:Yoomoney'))
async def refill_check_yoomoney(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_method = call.data.split(":")[1]
    pay_receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        YoomoneyAPI(
            bot=bot,
            arSession=arSession,
            update=call,
        )
    ).bill_check(pay_receipt)

    if pay_status == 0:
        get_refill = Refillx.get(refill_receipt=pay_receipt)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_method=pay_method,
                pay_amount=pay_amount,
                pay_receipt=pay_receipt,
                pay_comment=pay_receipt,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
            await call.message.edit_reply_markup()
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=30)
    elif pay_status == 2:
        await call.answer("❗️ Оплата не была найдена. Попробуйте позже", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗️ Оплата была произведена не в рублях", True, cache_time=5)
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


# Проверка оплаты - Cryptobot
@router.callback_query(F.data.startswith('Pay:Cryptobot'))
async def refill_check_cryptobot(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_method = call.data.split(":")[1]
    pay_comment = call.data.split(":")[2]

    pay_status, pay_amount = await (
        CryptobotAPI(
            bot=bot,
            arSession=arSession,
            update=call,
        )
    ).bill_check(pay_comment)

    if pay_status == 0:
        get_refill = Refillx.get(refill_comment=pay_comment)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_method=pay_method,
                pay_amount=pay_amount,
                pay_comment=pay_comment,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
            await call.message.edit_reply_markup()
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=30)
    elif pay_status == 2:
        await call.answer("❗️ Оплата не была найдена. Попробуйте позже", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗️ Вы не успели оплатить счёт", True, cache_time=5)
        await call.message.edit_reply_markup()
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


# Проверка оплаты - Cryptobot
@router.callback_query(F.data.startswith('Pay:Cryptocloud'))
async def refill_check_cryptocloud(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_method = call.data.split(":")[1]
    pay_comment = call.data.split(":")[2]

    pay_status, pay_amount = await (
        CryptocloudAPI(
            bot=bot,
            arSession=arSession,
            update=call,
        )
    ).bill_check(pay_comment)

    print(pay_status)

    if pay_status == 0:
        get_refill = Refillx.get(refill_comment=pay_comment)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_method=pay_method,
                pay_amount=pay_amount,
                pay_comment=pay_comment,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
            await call.message.edit_reply_markup()
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=30)
    elif pay_status == 2:
        await call.answer("❗️ Оплата не была найдена. Попробуйте позже", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗️ Счет был отменен", True, cache_time=5)
        await call.message.edit_reply_markup()
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


################################################################################
#################################### ПРОЧЕЕ ####################################
# Зачисление средств
async def refill_success(
        bot: Bot,
        call: CallbackQuery,
        pay_method: str,
        pay_amount: float,
        pay_receipt: Union[str, int] = None,
        pay_comment: str = None,
):
    get_user = Userx.get(user_id=call.from_user.id)

    if pay_receipt is None:
        pay_receipt = gen_id(10)
    if pay_comment is None:
        pay_comment = ""

    if pay_method == "Yoomoney":
        text_method = "ЮMoney"
    elif pay_method == "Cryptobot":
        text_method = "CryptoBot"
    elif pay_method == "Cryptocloud":
        text_method = "Cryptocloud"
    else:
        text_method = f"Unknown - {pay_method}"

    Refillx.add(
        user_id=get_user.user_id,
        refill_comment=pay_comment,
        refill_amount=pay_amount,
        refill_receipt=pay_receipt,
        refill_method=pay_method,
    )

    Userx.update(
        call.from_user.id,
        user_balance=round(get_user.user_balance + pay_amount, 2),
        user_refill=round(get_user.user_refill + pay_amount, 2),
    )

    await call.message.edit_text(
        ded(f"""
            <b>💰 Вы пополнили баланс на сумму <code>{pay_amount}₽</code>. Удачи ❤️
            🧾 Чек: <code>#{pay_receipt}</code></b>
        """)
    )

    await send_admins(
        bot,
        ded(f"""
            👤 Пользователь: <b>@{get_user.user_login}</b> | <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a> | <code>{get_user.user_id}</code>
            💰 Сумма пополнения: <code>{pay_amount}₽</code> <code>({text_method})</code>
            🧾 Чек: <code>#{pay_receipt}</code>
        """)
    )
