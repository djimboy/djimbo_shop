# - *- coding: utf- 8 - *-
import json
import time

from aiohttp import ClientConnectorCertificateError

from tgbot.keyboards.inline_main import close_inl
from tgbot.services.api_qiwip2p import QiwiAPIp2p
from tgbot.services.api_session import AsyncSession
from tgbot.services.api_sqlite import update_paymentx, get_paymentx
from tgbot.utils.const_functions import ded
from tgbot.utils.misc_functions import send_admins


# Апи работы с QIWI
class QiwiAPI:
    def __init__(
            self,
            dp,
            login=None,
            token=None,
            secret=None,
            pass_add=False,
            pass_check=False,
            pass_user=False,
    ):
        if login is not None:
            self.login = login
            self.token = token
            self.secret = secret
        else:
            self.login = get_paymentx()['qiwi_login']
            self.token = get_paymentx()['qiwi_token']
            self.secret = get_paymentx()['qiwi_secret']

        self.base_url = "https://edge.qiwi.com/{}/{}/persons/{}/{}"
        self.headers = {"authorization": f"Bearer {self.token}"}
        self.nickname = get_paymentx()['qiwi_nickname']
        self.pass_check = pass_check
        self.pass_user = pass_user
        self.pass_add = pass_add
        self.dp = dp

    # Рассылка админам о нерабочем киви
    @staticmethod
    async def error_wallet():
        await send_admins("<b>🥝 Qiwi кошелёк недоступен ❌</b>\n"
                          "❗ Как можно быстрее его замените")

    # Обязательная проверка перед каждым запросом
    async def pre_checker(self):
        if self.login != "None":
            if self.pass_add:
                status, response = await self.check_account()
            else:
                status, response, code = await self.check_logpass()

            if self.pass_add:
                if status:
                    update_paymentx(
                        qiwi_login=self.login,
                        qiwi_token=self.token,
                        qiwi_secret=self.secret
                    )

                await self.dp.edit_text(response)
            elif self.pass_check:
                if status:
                    if self.secret == "None":
                        text_secret = "Отсутствует"
                    else:
                        text_secret = self.secret

                    await self.dp.message.answer(f"<b>🥝 Qiwi кошелёк полностью функционирует ✅</b>\n"
                                                 f"◾ Номер: <code>{self.login}</code>\n"
                                                 f"◾ Токен: <code>{self.token}</code>\n"
                                                 f"◾ Приватный ключ: <code>{text_secret}</code>",
                                                 reply_markup=close_inl)
                    await self.dp.answer()
                else:
                    await self.error_wallet()
            elif self.pass_user:
                if not status:
                    await self.dp.edit_text(
                        "<b>❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                        "⌛ Попробуйте чуть позже.</b>")
                    await self.error_wallet()
                    return False
            elif not status:
                if not self.pass_add:
                    await self.error_wallet()
                    return False
            return True
        else:
            if self.pass_user:
                await self.dp.edit_text(
                    "<b>❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                    "⌛ Попробуйте чуть позже.</b>")
            await self.error_wallet()
            return False

    # Проверка баланса
    async def balance(self):
        response = await self.pre_checker()
        if response:
            status, response, code = await self._request(
                "funding-sources",
                "v2",
                "accounts",
            )

            save_balance = []
            for balance in response['accounts']:
                if "qw_wallet_usd" == balance['alias']:
                    save_balance.append(f"🇺🇸 Долларов: <code>{balance['balance']['amount']}$</code>")

                if "qw_wallet_rub" == balance['alias']:
                    save_balance.append(f"🇷🇺 Рублей: <code>{balance['balance']['amount']}₽</code>")

                if "qw_wallet_eur" == balance['alias']:
                    save_balance.append(f"🇪🇺 Евро: <code>{balance['balance']['amount']}€</code>")

                if "qw_wallet_kzt" == balance['alias']:
                    save_balance.append(f"🇰🇿 Тенге: <code>{balance['balance']['amount']}₸</code>")

            save_balance = "\n".join(save_balance)
            await self.dp.message.answer(f"<b>🥝 Баланс кошелька <code>{self.login}</code> составляет:</b>\n"
                                         f"{save_balance}",
                                         reply_markup=close_inl)
            await self.dp.answer()

    # Получение никнейма аккаунта
    async def get_nickname(self):
        response = await self.pre_checker()
        if response:
            status, response, code = await self._request(
                "qw-nicknames",
                "v1",
                "nickname",
            )

            if response['nickname'] is None:
                return False, "❗ На аккаунте отсутствует QIWI Никнейм. Установите его в настройках своего кошелька."
            else:
                return True, response['nickname']

        return False, ""

    # Проверка аккаунта (логпаса и п2п)
    async def check_account(self):
        status_history, response_history, code_history = await self.check_logpass()
        status_balance, response_balance, code_balance = await self._request(
            "funding-sources",
            "v2",
            "accounts"
        )

        if status_history and status_balance:
            if self.secret != "None":
                status_secret = await self.check_secret()
                if status_secret:
                    return True, "<b>🥝 QIWI кошелёк был успешно изменён ✅</b>"
                else:
                    return_message = ded(f"""
                                     <b>🥝 Введённые QIWI данные не прошли проверку ❌</b>
                                     ▶ Код ошибки: <code>Неверный приватный ключ</code>
                                     ❕ Указывайте ПРИВАТНЫЙ КЛЮЧ, а не публичный.
                                     Приватный ключ заканчивается на =
                                     """)
            else:
                return True, "<b>🥝 QIWI кошелёк был успешно изменён ✅</b>"
        else:
            if 400 in [code_history, code_balance]:
                return_message = ded(f"""
                                 <b>🥝 Введённые QIWI данные не прошли проверку ❌</b>
                                 ▶ Код ошибки: <code>Номер телефона указан в неверном формате</code>
                                 """)
            elif 401 in [code_history, code_balance]:
                return_message = ded(f"""
                                 <b>🥝 Введённые QIWI данные не прошли проверку ❌</b>
                                 ▶ Код ошибки: <code>Неверный токен или истек срок действия токена API</code>
                                 """)
            elif 403 in [code_history, code_balance]:
                return_message = ded(f"""
                                 <b>🥝 Введённые QIWI данные не прошли проверку ❌</b>
                                 ▶ <code>Ошибка: Нет прав на данный запрос (недостаточно разрешений у токена API)</code>
                                 """)
            elif "CERTIFICATE_VERIFY_FAILED" == code_history:
                return_message = ded(f"""
                                 <b>🥝 Введённые QIWI данные не прошли проверку ❌</b>
                                 ▶ Код ошибки: <code>CERTIFICATE_VERIFY_FAILED certificate verify failed: self signed certificate in certificate chain</code>
                                 ❗ Ваш сервер/дедик/устройство блокирует запросы к QIWI. Отключите антивирус или другие блокирующие ПО.
                                 """)
            else:
                return_message = ded(f"""
                                 <b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n
                                 ▶ Код ошибки: <code>{code_history}/{code_balance}</code>
                                 """)

        return False, return_message

    # Проверка логпаса киви
    async def check_logpass(self):
        status, response, code = await self._request(
            "payment-history",
            "v2",
            "payments",
            {"rows": 1, "operation": "IN"},
        )

        if status:
            if "data" in response:
                return True, response, code
            else:
                return False, None, code
        else:
            return False, None, code

    # Проверка п2п ключа
    async def check_secret(self):
        try:
            qiwi_p2p = QiwiAPIp2p(self.dp, self.secret)
            bill_id, bill_url = await qiwi_p2p.bill(3, lifetime=1)
            status = await qiwi_p2p.reject(bill_id=bill_id)
            return True
        except:
            return False

    # Генерация платежа
    async def bill(self, get_amount, get_way):
        response = await self.pre_checker()
        if response:
            bill_receipt = str(int(time.time() * 100))

            if get_way == "Form":
                qiwi_p2p = QiwiAPIp2p(self.dp, self.secret)
                bill_id, bill_url = await qiwi_p2p.bill(get_amount, bill_id=bill_receipt, lifetime=60)

                bill_message = ded(f"""
                               <b>💰 Пополнение баланса</b>
                               ➖➖➖➖➖➖➖➖➖➖
                               🥝 Для пополнения баланса, нажмите на кнопку ниже 
                               <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                               ❗ У вас имеется 60 минут на оплату счета.
                               💰 Сумма пополнения: <code>{get_amount}₽</code>
                               ➖➖➖➖➖➖➖➖➖➖
                               🔄 После оплаты, нажмите на <code>Проверить оплату</code>
                               """)
            elif get_way == "Number":
                bill_url = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={self.login}&amountInteger={get_amount}&amountFraction=0&extra%5B%27comment%27%5D={bill_receipt}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

                bill_message = ded(f"""
                               <b>💰 Пополнение баланса</b>
                               ➖➖➖➖➖➖➖➖➖➖
                               🥝 Для пополнения баланса, нажмите на кнопку ниже 
                               <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                               📞 QIWI кошелёк: <code>{self.login}</code>
                               🏷 Комментарий: <code>{bill_receipt}</code>
                               💰 Сумма пополнения: <code>{get_amount}₽</code>
                               ➖➖➖➖➖➖➖➖➖➖
                               🔄 После оплаты, нажмите на <code>Проверить оплату</code>
                               """)
            elif get_way == "Nickname":
                bill_url = f"https://qiwi.com/payment/form/99999?amountInteger={get_amount}&amountFraction=0&currency=643&extra%5B%27comment%27%5D={bill_receipt}&extra%5B%27account%27%5D={self.nickname}&blocked%5B0%5D=comment&blocked%5B1%5D=account&blocked%5B2%5D=sum&0%5Bextra%5B%27accountType%27%5D%5D=nickname"

                bill_message = ded(f"""
                               <b>💰 Пополнение баланса</b>
                               ➖➖➖➖➖➖➖➖➖➖
                               🥝 Для пополнения баланса, нажмите на кнопку ниже 
                               <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                               ❗ Не забудьте указать <u>КОММЕНТАРИЙ</u> к платежу
                               Ⓜ QIWI Никнейм: <code>{self.nickname}</code>
                               🏷 Комментарий: <code>{bill_receipt}</code>
                               💰 Сумма пополнения: <code>{get_amount}₽</code>
                               ➖➖➖➖➖➖➖➖➖➖
                               🔄 После оплаты, нажмите на <code>Проверить оплату</code>
                               """)

            return bill_message, bill_url, bill_receipt
        return False, False, False

    # Проверка платежа по форме
    async def check_form(self, receipt):
        qiwi_p2p = QiwiAPIp2p(self.dp, self.secret)
        bill_status, bill_amount = await qiwi_p2p.check(receipt)

        return bill_status, bill_amount

    # Проверка платежа по переводу
    async def check_send(self, receipt):
        response = await self.pre_checker()
        if response:
            status, response, code = await self._request(
                "payment-history",
                "v2",
                "payments",
                {"rows": 30, "operation": "IN"},
            )

            pay_status = False
            pay_amount = 0

            for check_pay in response['data']:
                if str(receipt) == str(check_pay['comment']):
                    if "643" == str(check_pay['sum']['currency']):
                        pay_status = True
                        pay_amount = int(float(check_pay['sum']['amount']))
                    else:
                        return_message = 1
                    break

            if pay_status:
                return_message = 3
            else:
                return_message = 2

            return return_message, pay_amount

        return 4, False

    # Сам запрос
    async def _request(self, action, version, get_way, params=None):
        url = self.base_url.format(action, version, self.login, get_way)

        aSession: AsyncSession = self.dp.bot['aSession']
        session = await aSession.get_session()

        try:
            response = await session.get(url, params=params, headers=self.headers, ssl=False)
            return True, json.loads((await response.read()).decode()), response.status
        except ClientConnectorCertificateError:
            return False, None, "CERTIFICATE_VERIFY_FAILED"
        except:
            return False, None, response.status
