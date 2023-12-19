# - *- coding: utf- 8 - *-
from typing import Union

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_payments import Paymentsx
from tgbot.database.db_refill import Refillx
from tgbot.database.db_users import Userx
from tgbot.keyboards.inline_user import refill_bill_finl, refill_method_finl
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_yoomoney import YoomoneyAPI
from tgbot.utils.const_functions import is_number, to_number, gen_id, ded
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import send_admins

min_refill_rub = 10  # Минимальная сумма пополнения в рублях

router = Router(name=__name__)


# Выбор способа пополнения
@router.callback_query(F.data == "user_refill")
async def refill_method(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_payment = Paymentsx.get()

    if get_payment.way_qiwi == "False" and get_payment.way_yoomoney == "False":
        return await call.answer("❗️ Пополнения временно недоступны", True)

    await call.message.edit_text(
        "<b>💰 Выберите способ пополнения</b>",
        reply_markup=refill_method_finl(),
    )


# Выбор способа пополнения
@router.callback_query(F.data.startswith("user_refill_method:"))
async def refill_method_select(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_method = call.data.split(":")[1]

    await state.update_data(here_pay_method=pay_method)

    await state.set_state("here_refill_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")


################################################################################
################################### ВВОД СУММЫ #################################
# Принятие суммы для пополнения средств
@router.message(F.text, StateFilter("here_refill_amount"))
async def refill_amount_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно.</b>\n"
            "💰 Введите сумму для пополнения средств",
        )

    if to_number(message.text) < min_refill_rub or to_number(message.text) > 100_000:
        return await message.answer(
            f"<b>❌ Неверная сумма пополнения</b>\n"
            f"❗️ Cумма не должна быть меньше <code>{min_refill_rub}₽</code> и больше <code>100 000₽</code>\n"
            f"💰 Введите сумму для пополнения средств",
        )

    cache_message = await message.answer("<b>♻️ Подождите, платёж генерируется...</b>")

    pay_amount = to_number(message.text)
    pay_method = (await state.get_data())['here_pay_method']
    await state.clear()

    if pay_method == "QIWI":
        bill_message, bill_link, bill_receipt = await (
            QiwiAPI(
                bot=bot,
                arSession=arSession,
            )
        ).bill(pay_amount)
    elif pay_method == "Yoomoney":
        bill_message, bill_link, bill_receipt = await (
            YoomoneyAPI(
                bot=bot,
                arSession=arSession,
            )
        ).bill(pay_amount)

    if bill_message:
        await cache_message.edit_text(
            bill_message,
            reply_markup=refill_bill_finl(bill_link, bill_receipt, pay_method),
        )


################################################################################
############################### ПРОВЕРКА ПЛАТЕЖЕЙ ##############################
# Проверка оплаты - ЮMoney
@router.callback_query(F.data.startswith('Pay:Yoomoney'))
async def refill_check_yoomoney(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_way = call.data.split(":")[1]
    pay_receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        YoomoneyAPI(
            bot=bot,
            arSession=arSession,
        )
    ).bill_check(pay_receipt)

    if pay_status == 0:
        get_refill = Refillx.get(refill_receipt=pay_receipt)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_way=pay_way,
                pay_amount=pay_amount,
                pay_receipt=pay_receipt,
                pay_comment=pay_receipt,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗️ Платёж не был найден. Попробуйте позже", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗️ Оплата была произведена не в рублях", True, cache_time=5)
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


# Проверка оплаты - QIWI
@router.callback_query(F.data.startswith('Pay:QIWI'))
async def refill_check_qiwi(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_way = call.data.split(":")[1]
    pay_receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        QiwiAPI(
            bot=bot,
            arSession=arSession,
        )
    ).bill_check(pay_receipt)

    if pay_status == 0:
        get_refill = Refillx.get(refill_receipt=pay_receipt)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_way=pay_way,
                pay_amount=pay_amount,
                pay_receipt=pay_receipt,
                pay_comment=pay_receipt,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗ Платёж не был найден. Попробуйте позже.", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗ Оплата была произведена не в рублях.", True, cache_time=5)
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


################################################################################
#################################### ПРОЧЕЕ ####################################
# Зачисление средств
async def refill_success(
        bot: Bot,
        call: CallbackQuery,
        pay_way: str,
        pay_amount: float,
        pay_receipt: Union[str, int] = None,
        pay_comment: str = None,
):
    get_user = Userx.get(user_id=call.from_user.id)

    if pay_receipt is None:
        pay_receipt = gen_id()
    if pay_comment is None:
        pay_comment = ""

    Refillx.add(
        user_id=get_user.user_id,
        refill_comment=pay_comment,
        refill_amount=pay_amount,
        refill_receipt=pay_receipt,
        refill_method=pay_way,
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
            💰 Сумма пополнения: <code>{pay_amount}₽</code>
            🧾 Чек: <code>#{pay_receipt}</code>
        """)
    )
