# - *- coding: utf- 8 - *-
import json
import random
import time

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pyqiwip2p import QiwiP2P

from keyboards.default import all_back_to_main_default, check_user_out_func
from keyboards.inline import *
from loader import dp, bot
from states.state_payment import StorageQiwi
from utils import send_all_admin, clear_firstname, get_dates
from utils.db_api.sqlite import update_userx, get_refillx, add_refillx


###################################################################################
############################## ВВОД СУММЫ ПОПОЛНЕНИЯ ##############################
# Выбор способа пополнения
@dp.callback_query_handler(text="user_input", state="*")
async def input_amount(call: CallbackQuery, state: FSMContext):
    check_pass = False
    get_payment = get_paymentx()
    if get_payment[5] == "True":
        if get_payment[0] != "None" and get_payment[1] != "None" and get_payment[2] != "None":
            try:
                request = requests.Session()
                request.headers["authorization"] = "Bearer " + get_payment[1]
                response_qiwi = request.get(
                    f"https://edge.qiwi.com/payment-history/v2/persons/{get_payment[0]}/payments",
                    params={"rows": 1, "operation": "IN"})
                if response_qiwi.status_code == 200:
                    await StorageQiwi.here_input_qiwi_amount.set()
                    await bot.delete_message(call.from_user.id, call.message.message_id)
                    await call.message.answer("<b>💵 Введите сумму для пополнения средств 🥝</b>",
                                              reply_markup=all_back_to_main_default)
                else:
                    check_pass = True
            except json.decoder.JSONDecodeError:
                check_pass = True

            if check_pass:
                await bot.answer_callback_query(call.id, "❗ Пополнение временно недоступно")
                await send_all_admin(
                    f"👤 Пользователь <a href='tg://user?id={call.from_user.id}'>{clear_firstname(call.from_user.first_name)}</a> "
                    f"пытался пополнить баланс.\n"
                    f"<b>❌ QIWI кошелёк не работает. Срочно замените его.</b>")
        else:
            await bot.answer_callback_query(call.id, "❗ Пополнение временно недоступно")
            await send_all_admin(
                f"👤 Пользователь <a href='tg://user?id={call.from_user.id}'>{clear_firstname(call.from_user.first_name)}</a> "
                f"пытался пополнить баланс.\n"
                f"<b>❌ QIWI кошелёк недоступен. Срочно замените его.</b>")
    else:
        await bot.answer_callback_query(call.id, "❗ Пополнения в боте временно отключены")


###################################################################################
####################################### QIWI ######################################
# Принятие суммы для пополнения средств через QIWI
@dp.message_handler(state=StorageQiwi.here_input_qiwi_amount)
async def create_qiwi_pay(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        pay_amount = int(message.text)
        del_msg = await bot.send_message(message.from_user.id, "<b>♻ Подождите, платёж генерируется...</b>")
        min_input_qiwi = 1  # Минимальная сумма пополнения в рублях

        get_payments = get_paymentx()
        if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
            try:
                request = requests.Session()
                request.headers["authorization"] = "Bearer " + get_payments[1]
                response_qiwi = request.get(
                    f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
                    params={"rows": 1, "operation": "IN"})
                if pay_amount >= min_input_qiwi:
                    passwd = list("1234567890ABCDEFGHIGKLMNOPQRSTUVYXWZ")
                    random.shuffle(passwd)
                    random_chars = "".join([random.choice(passwd) for x in range(10)])
                    generate_number_check = str(random.randint(100000000000, 999999999999))
                    if get_payments[4] == "form":
                        qiwi = QiwiP2P(get_payments[2])
                        bill = qiwi.bill(bill_id=generate_number_check, amount=pay_amount,
                                         comment=generate_number_check)
                        way_pay = "Form"
                        send_requests = bill.pay_url
                        send_message = f"<b>🆙 Пополнение баланса</b>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"❗ У вас имеется 30 минут на оплату счета.\n" \
                                       f"🥝 Для пополнения баланса, нажмите на кнопку  <code>Перейти к оплате</code>\n" \
                                       f"💵 Сумма пополнения: <code>{pay_amount}руб</code>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
                    elif get_payments[4] == "number":
                        way_pay = "Number"
                        send_requests = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={get_payments[0]}&amountInteger=" \
                                        f"{pay_amount}&amountFraction=0&extra%5B%27comment%27%5D={generate_number_check}&currency=" \
                                        f"643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"
                        send_message = f"<b>🆙 Пополнение баланса</b>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🥝 Для пополнения баланса, переведите нужную сумму на указанный кошелёк или " \
                                       f"нажмите на кнопку  <code>Перейти к оплате</code>\n" \
                                       f"❗ Обязательно введите комментарий, который указан ниже\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🏷 Комментарий: <code>{generate_number_check}</code>\n" \
                                       f"📞 QIWI кошелёк: <code>{get_payments[0]}</code>\n" \
                                       f"💵 Сумма пополнения: <code>{pay_amount}руб</code>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
                    elif get_payments[4] == "nickname":
                        way_pay = "Nickname"
                        send_requests = f"https://qiwi.com/payment/form/99999?amountInteger={pay_amount}&amountFraction=0&currency=643" \
                                        f"&extra%5B%27comment%27%5D=405550&extra%5B%27account%27%5D={get_payments[3]}&blocked%5B0%5D=" \
                                        f"comment&blocked%5B1%5D=account&blocked%5B2%5D=sum&0%5Bextra%5B%27accountType%27%5D%5D=nickname"
                        # send_requests = short_link.get(f"https://clck.ru/--?url={send_requests}").text
                        send_message = f"<b>🆙 Пополнение баланса</b>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🥝 Для пополнения баланса, переведите нужную сумму на указанный кошелёк или " \
                                       f"нажмите на кнопку  <code>Перейти к оплате</code> и укажите комментарий\n" \
                                       f"❗ Обязательно введите комментарий, который указан ниже\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🏷 Комментарий: <code>{generate_number_check}</code>\n" \
                                       f"Ⓜ QIWI Никнейм: <code>{get_payments[3]}</code>\n" \
                                       f"💵 Сумма пополнения: <code>{pay_amount}руб</code>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
                    await bot.delete_message(message.chat.id, del_msg.message_id)
                    delete_msg = await message.answer("🥝 <b>Платёж был создан.</b>",
                                                      reply_markup=check_user_out_func(message.from_user.id))
                    await message.answer(send_message,
                                         reply_markup=create_pay_qiwi_func(send_requests,
                                                                           generate_number_check,
                                                                           delete_msg.message_id,
                                                                           way_pay))
                    await state.finish()
                else:
                    await StorageQiwi.here_input_qiwi_amount.set()
                    await bot.delete_message(message.chat.id, del_msg.message_id)
                    await message.answer(f"❌ <b>Неверная сумма пополнения</b>\n"
                                         f"▶ Мин. сумма пополнения: <code>{min_input_qiwi}руб</code>\n"
                                         f"💵 Введите сумму для пополнения средств 🥝")
            except json.decoder.JSONDecodeError or UnicodeEncodeError:
                await state.finish()
                await bot.delete_message(message.chat.id, del_msg.message_id)
                await message.answer("❕ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                                     "⌛ Попробуйте чуть позже.",
                                     reply_markup=check_user_out_func(message.from_user.id))
                await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                     f"❕ <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>"
                                     " пытался пополнить баланс\n"
                                     "❗ Как можно быстрее замените QIWI кошелёк")
        else:
            await state.finish()
            await bot.delete_message(message.chat.id, del_msg.message_id)
            await message.answer("❕ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                                 "⌛ Попробуйте чуть позже.",
                                 reply_markup=check_user_out_func(message.from_user.id))
            await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                 f"❕ <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>"
                                 " пытался пополнить баланс\n"
                                 "❗ Как можно быстрее замените QIWI кошелёк")
    else:
        await StorageQiwi.here_input_qiwi_amount.set()
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💵 Введите сумму для пополнения средств 🥝")


# Обработка колбэка "Проверить оплату" QIWI через Форму
@dp.callback_query_handler(text_startswith="Pay:Form:")
async def check_qiwi_pay(call: CallbackQuery):
    receipt = call.data[9:].split(":")[0]
    message_id = call.data[9:].split(":")[1]
    get_payments = get_paymentx()
    get_user_info = get_userx(user_id=call.from_user.id)
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        qiwi = QiwiP2P(get_payments[2])
        pay_comment = qiwi.check(bill_id=receipt).comment  # Получение комментария платежа
        pay_status = qiwi.check(bill_id=receipt).status  # Получение статуса платежа
        pay_amount = float(qiwi.check(bill_id=receipt).amount)  # Получение суммы платежа в рублях
        pay_amount = int(pay_amount)
        if pay_status == "PAID":
            get_purchase = get_refillx("*", receipt=receipt)
            if get_purchase is None:

                add_refillx(call.from_user.id, call.from_user.username, call.from_user.first_name, pay_comment,
                            pay_amount, receipt, "Form", get_dates(),
                            int(time.time()))

                # Обновление баланса у пользователя
                update_userx(call.from_user.id,
                             balance=int(get_user_info[4]) + pay_amount,
                             all_refill=int(get_user_info[5]) + pay_amount)

                await bot.delete_message(call.message.chat.id, message_id)
                await call.message.delete()
                await call.message.answer(f"<b>✅ Вы успешно пополнили баланс на сумму {pay_amount}руб. Удачи ❤</b>\n"
                                          f"<b>📃 Чек:</b> <code>+{receipt}</code>",
                                          reply_markup=check_user_out_func(call.from_user.id))
                await send_all_admin(f"<b>💰 Пользователь</b> "
                                     f"(@{call.from_user.username}|<a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a>"
                                     f"|<code>{call.from_user.id}</code>) "
                                     f"<b>пополнил баланс на сумму</b> <code>{pay_amount}руб</code> 🥝\n"
                                     f"📃 <b>Чек:</b> <code>+{receipt}</code>")
            else:
                await bot.answer_callback_query(call.id, "❗ Ваше пополнение уже зачислено.", True)
        elif pay_status == "EXPIRED":
            await bot.edit_message_text("<b>❌ Время оплаты вышло. Платёж был удалён.</b>",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=check_user_out_func(call.from_user.id))
        elif pay_status == "WAITING":
            await bot.answer_callback_query(call.id, "❗ Оплата не была произведена.", True)
        elif pay_status == "REJECTED":
            await bot.edit_message_text("<b>❌ Счёт был отклонён.</b>",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=check_user_out_func(call.from_user.id))
    else:
        await send_all_admin("<b>❗ Кто-то пытался проверить платёж, но QIWI не работает\n"
                             "❗ Срочно замените QIWI данные</b>")
        await bot.answer_callback_query(call.id, "❗ Извиняемся за доставленные неудобства,\n"
                                                 "проверка платежа временно недоступна.\n"
                                                 "⏳ Попробуйте чуть позже.")


# Обработка колбэка "Проверить оплату" QIWI через Номер и Никнейм
@dp.callback_query_handler(text_startswith=["Pay:Number", "Pay:Nickname"])
async def check_qiwi_pay(call: CallbackQuery):
    way_pay = call.data[4:].split(":")[0]
    receipt = call.data[4:].split(":")[1]
    message_id = call.data[4:].split(":")[2]
    get_payments = get_paymentx()
    get_user_info = get_userx(user_id=call.from_user.id)
    pay_status = False
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        try:
            request = requests.Session()
            request.headers["authorization"] = "Bearer " + get_payments[1]
            get_history = request.get(
                f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
                params={"rows": 20, "operation": "IN"}).json()["data"]
            for check_pay in get_history:
                if str(receipt) == str(check_pay["comment"]):
                    if "643" == str(check_pay["sum"]["currency"]):
                        pay_status = True  # Получение статуса платежа
                        pay_amount = float(check_pay["sum"]["amount"])  # Получение суммы платежа в рублях
                        pay_amount = int(pay_amount)
                    else:
                        await bot.answer_callback_query(call.id, "❗ Оплата была произведена не в рублях.", True)
            if pay_status:
                get_purchase = get_refillx("*", receipt=receipt)
                if get_purchase is None:
                    add_refillx(call.from_user.id, call.from_user.username, call.from_user.first_name, receipt,
                                pay_amount, receipt, way_pay, get_dates(), int(time.time()))

                    # Обновление баланса у пользователя
                    update_userx(call.from_user.id,
                                 balance=int(get_user_info[4]) + pay_amount,
                                 all_refill=int(get_user_info[5]) + pay_amount)

                    await bot.delete_message(call.message.chat.id, message_id)
                    await call.message.delete()
                    await call.message.answer(
                        f"<b>✅ Вы успешно пополнили баланс на сумму {pay_amount}руб. Удачи ❤</b>\n"
                        f"<b>📃 Чек:</b> <code>+{receipt}</code>",
                        reply_markup=check_user_out_func(call.from_user.id))
                    await send_all_admin(f"<b>💰 Пользователь</b> "
                                         f"(@{call.from_user.username}|<a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a>"
                                         f"|<code>{call.from_user.id}</code>) "
                                         f"<b>пополнил баланс на сумму</b> <code>{pay_amount}руб</code> 🥝\n"
                                         f"📃 <b>Чек:</b> <code>+{receipt}</code>")
                else:
                    await bot.answer_callback_query(call.id, "❗ Ваше пополнение уже зачислено.", True)
            else:
                await bot.answer_callback_query(call.id, "❗ Платёж не был найден.\n⌛ Попробуйте чуть позже.", True)
        except json.decoder.JSONDecodeError:
            await bot.answer_callback_query(call.id,
                                            "❕ Извиняемся за доставленные неудобства, проверка временно недоступна.\n"
                                            "⌛ Попробуйте чуть позже.", True)
            await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                 f"❕ <a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a>"
                                 " пытался проверить платёж\n"
                                 "❗ Как можно быстрее замените QIWI кошелёк")
    else:
        await send_all_admin("<b>❗ Кто-то пытался проверить платёж, но QIWI не работает\n"
                             "❗ Срочно замените QIWI данные</b>")
        await bot.answer_callback_query(call.id, "❗ Извиняемся за доставленные неудобства,\n"
                                                 "проверка платежа временно недоступна.\n"
                                                 "⏳ Попробуйте чуть позже.")
