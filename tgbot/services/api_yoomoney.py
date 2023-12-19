# - *- coding: utf- 8 - *-
import json
from typing import Union

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiohttp import ClientConnectorCertificateError

from tgbot.database.db_payments import Paymentsx
from tgbot.utils.const_functions import ded, gen_id, send_errors
from tgbot.utils.misc.bot_models import ARS
from tgbot.utils.misc_functions import send_admins


class YoomoneyAPI:
    def __init__(
            self,
            bot: Bot,
            arSession: ARS,
            update: Union[Message, CallbackQuery] = None,
            token: str = None,
            skipping_error: bool = False,
    ):
        if token is not None:
            self.token = token
        else:
            get_payment = Paymentsx.get()

            self.token = get_payment.yoomoney_token

        self.base_url = 'https://yoomoney.ru/api/'
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        self.bot = bot
        self.arSession = arSession
        self.update = update
        self.token = token
        self.skipping_error = skipping_error

    # Рассылка админам о нерабочем кошельке
    async def error_wallet_admin(self, error_code: str = "Unknown"):
        if not self.skipping_error:
            await send_admins(
                self.bot,
                f"<b>🔮 ЮMoney недоступен. Как можно быстрее его замените</b>\n"
                f"❗️ Error: <code>{error_code}</code>"
            )

    # Уведомление пользователям о неполадках с пополнением
    async def error_wallet_user(self):
        if self.update is not None and not self.skipping_error:
            if isinstance(self.update, Message):
                await self.update.edit_text(
                    "<b>❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                    "⌛ Попробуйте чуть позже.</b>"
                )
            elif isinstance(self.update, CallbackQuery):
                await self.update.answer(
                    "❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                    "⌛ Попробуйте чуть позже."
                )
            else:
                await send_errors(self.bot, 4938221)

    # Проверка кошелька
    async def check(self) -> str:
        status, response = await self._request("account-info")

        if status:
            if len(response) >= 1:
                if response['identified']:
                    text_identified = "Присутствует"
                else:
                    text_identified = "Отсутствует"

                if response['account_status'] == "identified":
                    text_status = "Идентифицированный счет"
                elif response['account_status'] == "anonymous":
                    text_status = "Анонимный счет"
                elif response['account_status'] == "named":
                    text_status = "Именной счет"
                else:
                    text_status = response['account_status']

                if response['account_type'] == "personal":
                    text_type = "Пользовательский счет"
                elif response['account_type'] == "professional":
                    text_type = "Профессиональный счет"
                else:
                    text_type = response['account_type']

                return ded(f"""
                    <b>🔮 ЮMoney кошелёк полностью функционирует ✅</b>
                    ➖➖➖➖➖➖➖➖➖➖
                    ▪️ Кошелёк: <code>{response['account']}</code>
                    ▪️ Идентификация: <code>{text_identified}</code>
                    ▪️ Статус аккаунта: <code>{text_status}</code>
                    ▪️ Тип счета: <code>{text_type}</code>
                """)
            else:
                return "<b>🔮 Не удалось проверить ЮMoney кошелёк ❌</b>"
        else:
            return "<b>🔮 Не удалось проверить ЮMoney кошелёк ❌</b>"

    # Получение баланса
    async def balance(self) -> str:
        status, response = await self._request("account-info")

        if status:
            wallet_balance = response['balance']
            wallet_number = await self.account_info()

            return ded(f"""
                <b>🔮 Баланс кошелька ЮMoney</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Кошелёк: <code>{wallet_number}</code>
                ▪️ Баланс: <code>{wallet_balance}₽</code>
            """)
        else:
            return "<b>🔮 Не удалось получить баланс ЮMoney кошелька ❌</b>"

    # Информация об аккаунте
    async def account_info(self):
        status, response = await self._request("account-info")

        return response['account']

    # Получение ссылки на авторизацию
    async def authorization_get(self) -> str:
        session = await self.arSession.get_session()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        url = f"https://yoomoney.ru/oauth/authorize?client_id=DC7FFCDA285C720D958E6EB6FB4910335C186CB6C8539A1686B5E109128562AB&response_type=code&redirect_uri=https://yoomoney.ru&scope=account-info%20operation-history%20operation-details"

        response = await session.post(url, headers=headers)

        return str(response.url)

    # Принятие кода авторизации и получение токена
    async def authorization_enter(self, get_code: str) -> tuple[bool, str, str]:
        session = await self.arSession.get_session()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        url = f"https://yoomoney.ru/oauth/token?code={get_code}&client_id=DC7FFCDA285C720D958E6EB6FB4910335C186CB6C8539A1686B5E109128562AB&grant_type=authorization_code&redirect_uri=https://yoomoney.ru"

        response = await session.post(url, headers=headers)
        response_data = json.loads((await response.read()).decode())

        if "error" in response_data:
            error = response_data['error']

            if error == "invalid_request":
                return False, "", "<b>❌ Требуемые параметры запроса отсутствуют или имеют неправильные или недопустимые значения</b>"
            elif error == "unauthorized_client":
                return False, "", ded(f"""
                    <b>❌ Недопустимое значение параметра 'client_id' или 'client_secret', или приложение
                    не имеет права запрашивать авторизацию (например, ЮMoney заблокировал его 'client_id')</b>
                """)
            elif error == "invalid_grant":
                return False, "", ded(f"""
                    <b>❌ В выпуске 'access_token' отказано. ЮMoney не выпускал временный токен,
                    срок действия токена истек, или этот временный токен уже выдан
                    'access_token' (повторный запрос токена авторизации с тем же временным токеном)</b>
                """)

        if response_data['access_token'] == "":
            return False, "", "<b>❌ Не удалось получить токен. Попробуйте всё снова.</b>"

        return True, response_data['access_token'], "<b>🔮 ЮMoney кошелёк был успешно изменён ✅</b>"

    # Создание платежа
    async def bill(self, pay_amount: Union[float, int]) -> tuple[str, str, int]:
        session = await self.arSession.get_session()

        bill_receipt = gen_id()

        get_wallet = await self.account_info()
        url = "https://yoomoney.ru/quickpay/confirm.xml?"

        pay_amount_bill = pay_amount + (pay_amount * 0.031)

        if float(pay_amount_bill) < 2:
            pay_amount_bill = 2.04

        payload = {
            'receiver': get_wallet,
            'quickpay_form': "button",
            'targets': 'Добровольное пожертвование',
            'paymentType': 'SB',
            'sum': pay_amount_bill,
            'label': bill_receipt,
        }

        for value in payload:
            url += str(value).replace("_", "-") + "=" + str(payload[value])
            url += "&"

        bill_link = str((await session.post(url[:-1].replace(" ", "%20"))).url)

        bill_message = ded(f"""
            <b>💰 Пополнение баланса</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Для пополнения баланса, нажмите на кнопку ниже 
            <code>Перейти к оплате</code> и оплатите выставленный вам счёт
            ▪️ У вас имеется 60 минут на оплату счета.
            ▪️ Сумма пополнения: <code>{pay_amount}₽</code>
            ➖➖➖➖➖➖➖➖➖➖
            ❗️ После оплаты, нажмите на <code>Проверить оплату</code>
        """)

        return bill_message, bill_link, bill_receipt

    # Проверка платежа
    async def bill_check(self, receipt: Union[str, int] = None, records: int = 1) -> tuple[int, float]:
        data = {
            'type': 'deposition',
            'details': 'true',
        }

        if receipt is not None:
            data['label'] = receipt
        if records is not None:
            data['records'] = records

        status, response = await self._request("operation-history", data)

        pay_status = 1
        pay_amount = None
        pay_currency = None

        if status:
            pay_status = 2

            if len(response['operations']) >= 1:
                pay_currency = response['operations'][0]['amount_currency']
                pay_amount = response['operations'][0]['amount']

                pay_status = 3

                if pay_currency == "RUB":
                    pay_status = 0

        return pay_status, pay_amount

    # Запрос
    async def _request(
            self,
            method: str,
            data: dict = None,
    ) -> tuple[bool, any]:
        session = await self.arSession.get_session()

        url = self.base_url + method

        try:
            response = await session.post(url, headers=self.headers, data=data)
            response_data = json.loads((await response.read()).decode())

            if response.status == 200:
                return True, response_data
            else:
                await self.error_wallet_user()
                await self.error_wallet_admin(f"{response.status} - {str(response_data)}")

                return False, response_data
        except ClientConnectorCertificateError:
            await self.error_wallet_user()
            await self.error_wallet_admin("CERTIFICATE_VERIFY_FAILED")

            return False, "CERTIFICATE_VERIFY_FAILED"
        except Exception as ex:
            await self.error_wallet_user()
            await self.error_wallet_admin(str(ex))

            return False, str(ex)
