# - *- coding: utf- 8 - *-
import json
from typing import Union

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiohttp import ClientConnectorCertificateError

from tgbot.database import Paymentsx
from tgbot.utils.const_functions import ded, to_number
from tgbot.utils.misc.bot_models import ARS
from tgbot.utils.misc_functions import send_admins


class CryptocloudAPI:
    def __init__(
            self,
            bot: Bot,
            arSession: ARS,
            update: Union[Message, CallbackQuery] = None,
            token: str = None,
            shop_id: str = None,
            skipping_error: bool = False,
    ):
        if token is not None:
            self.token = token
            self.adding = True
        else:
            self.token = Paymentsx.get().cryptocloud_token
            self.adding = False

        if shop_id is not None:
            self.shop_id = shop_id
            self.adding = True
        else:
            self.shop_id = Paymentsx.get().cryptocloud_shop_id
            self.adding = False

        self.base_url = 'https://api.cryptocloud.plus/v2/'
        self.headers = {
            'Authorization': f"Token {self.token}",
            'Content-Type': 'application/json',
        }

        self.bot = bot
        self.arSession = arSession
        self.update = update
        self.skipping_error = skipping_error

    # Уведомления о нерабочем кошельке
    async def error_notification(self, error_code: str = "Unknown"):
        if not self.skipping_error:
            if self.adding:
                await self.update.edit_text(
                    f"<b>🔷 Не удалось добавить Cryptocloud ❌</b>\n"
                    f"❗️ Ошибка: <code>{error_code}</code>"
                )
            else:
                await send_admins(
                    self.bot,
                    f"<b>🔷 Cryptocloud недоступен. Как можно быстрее его замените</b>\n"
                    f"❗️ Ошибка: <code>{error_code}</code>"
                )

    # Проверка кошелька
    async def check(self) -> tuple[bool, str]:
        payload = {
            'amount': '1',
            'shop_id': self.shop_id,
            "currency": 'RUB'
        }

        status, response, = await self._request("invoice/create", payload)

        if status and 'result' in response:
            status, response, = await self._request("invoice/merchant/canceled", {"uuid": response["result"]["uuid"]})
            return True, ded(f"""
                <b>₿ Cryptocloud полностью функционирует ✅</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Токен: <code>{self.token}</code>
                ▪️ Shop ID: <code>{self.shop_id}</code>
            """)

        return False, "<b>₿ Не удалось проверить Cryptocloud ❌</b>"

    # Получение баланса
    async def balance(self) -> str:
        status, response = await self._request("merchant/wallet/balance/all")

        total_balance_usd = 0
        total_available_balance_usd = 0
        if status and 'result' in response:
            for currency in response['result']:
                total_balance_usd += currency['balance_usd']
                total_available_balance_usd += currency['available_balance_usd']

            return ded(f"""
                <b>₿ Баланс Cryptocloud</b>
                ➖➖➖➖➖➖➖➖➖➖
                <b>Общий:</b> <i>${total_balance_usd}</i>
                <b>Доступный:</b> <i>${total_available_balance_usd}</i>
            """)

        return "<b>₿ Не удалось получить баланс Cryptocloud ❌</b>"

    # Создание платежа
    async def bill(self, pay_amount: Union[float, int]) -> tuple[Union[str, bool], str, str]:

        payload = {
            'amount': str(pay_amount),
            'shop_id': self.shop_id,
            "currency": 'RUB'
        }

        status, response, = await self._request("invoice/create", payload)

        if status and 'result' in response:
            bill_message = ded(f"""
                <b>💰 Пополнение баланса</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Для пополнения баланса, нажмите на кнопку ниже 
                <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                ▪️ У вас имеется 24 часа на оплату счета
                ▪️ Сумма пополнения: <code>{pay_amount}₽</code>
                ➖➖➖➖➖➖➖➖➖➖
                ❗️ После оплаты, нажмите на <code>Проверить оплату</code>
            """)

            return bill_message, response['result']['link'], response['result']['uuid']

        return False, "", ""

    # Проверка платежа
    async def bill_check(self, bill_receipt: Union[str, int] = None) -> tuple[int, float]:
        payload = {
            'uuids': [bill_receipt],
        }

        status, response = await self._request("invoice/merchant/info", payload)

        pay_status, pay_amount = 1, 0
        

        if status and 'result' in response:
            get_invoice = response['result'][0]

            if get_invoice['invoice_status'] == "created":
                pay_status = 2
            elif get_invoice['invoice_status'] == "canceled":
                pay_status = 3
            elif get_invoice['invoice_status'] == "canceled" or get_invoice['invoice_status'] == "overpaid":
                pay_status = 0
                pay_amount = to_number(get_invoice['amount_in_fiat'])
            else:
                pay_status = 4

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
            response = await session.post(
                url=url,
                headers=self.headers,
                json=data,
                ssl=False,
            )

            response_data = json.loads((await response.read()).decode())

            if response.status == 200:
                return True, response_data
            else:
                await self.error_notification(f"{response.status} - {str(response_data)}")

                return False, response_data
        except ClientConnectorCertificateError:
            await self.error_notification("CERTIFICATE_VERIFY_FAILED")

            return False, "CERTIFICATE_VERIFY_FAILED"
        except Exception as ex:
            await self.error_notification(str(ex))

            return False, str(ex)
