# - *- coding: utf- 8 - *-
import json
from typing import Union

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientConnectorCertificateError

from tgbot.database.db_payments import Paymentsx
from tgbot.utils.const_functions import ded, send_errors, gen_id
from tgbot.utils.misc.bot_models import ARS
from tgbot.utils.misc_functions import send_admins


# Апи работы с QIWI
class QiwiAPI:
    def __init__(
            self,
            bot: Bot,
            arSession: ARS,
            update: Union[Message, CallbackQuery] = None,
            login: str = None,
            token: str = None,
            skipping_error: bool = False,
    ):
        if login is not None:
            self.login = login
            self.token = token
        else:
            get_payment = Paymentsx.get()

            self.login = get_payment.qiwi_login
            self.token = get_payment.qiwi_token

        self.headers = {
            'authorization': f'Bearer {self.token}',
        }

        self.bot = bot
        self.arSession = arSession
        self.update = update
        self.skipping_error = skipping_error

    # Рассылка админам о нерабочем кошельке
    async def error_wallet_admin(self, error_code: str = "Unknown"):
        if not self.skipping_error:
            await send_admins(
                self.bot,
                f"<b>🥝 QIWI недоступен. Как можно быстрее его замените</b>\n"
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
                await send_errors(self.bot, 4934355)

    # Проверка баланса
    async def balance(self) -> str:
        url = f"https://edge.qiwi.com/funding-sources/v2/persons/{self.login}/accounts"

        status, response, code = await self._request("GET", url)

        if status:
            save_balance = []

            for balance in response['accounts']:
                if "qw_wallet_usd" == balance['alias']:
                    save_balance.append(f"🇺🇸 Баланс в Долларах: <code>{balance['balance']['amount']}$</code>")

                if "qw_wallet_rub" == balance['alias']:
                    save_balance.append(f"🇷🇺 Баланс в Рублях: <code>{balance['balance']['amount']}₽</code>")

                if "qw_wallet_eur" == balance['alias']:
                    save_balance.append(f"🇪🇺 Баланс в Евро: <code>{balance['balance']['amount']}€</code>")

                if "qw_wallet_kzt" == balance['alias']:
                    save_balance.append(f"🇰🇿 Баланс в Тенге: <code>{balance['balance']['amount']}₸</code>")

            save_balance = "\n".join(save_balance)

            return ded(f"""
                <b>🥝 Баланс кошелька QIWI</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Кошелёк: <code>{self.login}</code>
                {save_balance}
            """)
        else:
            return ded(f"""
                <b>🥝 Не удалось получить баланс QIWI кошелька ❌</b>
                ❗️ Error 4377125: <code>{response}</code>
            """)

    # Проверка лимитов у аккаунта
    async def check_limits(self) -> bool:
        url = f"https://edge.qiwi.com/person-profile/v1/persons/{self.login}/status/restrictions"

        status, response, code, = await self._request("GET", url)

        if response is not None and len(response) == 0:
            return False
        else:
            return True

    # Проверка кошелька
    async def check(self) -> tuple[bool, str]:
        url = "https://edge.qiwi.com/person-profile/v1/profile/current"

        status, response, code = await self._request("GET", url)

        if status:
            status_limit = await self.check_limits()

            # Наличие лимитов
            if status_limit:
                text_limit = "Присутствуют"
            else:
                text_limit = "Отсутствуют"

            # Уровень идентификации
            for account in response['contractInfo']['identificationInfo']:
                if account['bankAlias'] == "QIWI":
                    if account['identificationLevel'] == "ANONYMOUS":
                        text_identification = "Без идентификации"
                    elif account['identificationLevel'] == "SIMPLE":
                        text_identification = "Упрощенная идентификация"
                    elif account['identificationLevel'] == "VERIFIED":
                        text_identification = "Упрощенная идентификация"
                    elif account['identificationLevel'] == "FULL":
                        text_identification = "Полная идентификации"
                    else:
                        text_identification = account['identificationLevel']

            # СМС оповещения
            if response['contractInfo']['smsNotification']['enabled']:
                text_notification = "Включены"
            else:
                text_notification = "Отключены"

            return True, ded(f"""
                <b>🥝 QIWI кошелёк полностью функционирует ✅</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Кошелёк: <code>{self.login}</code>
                ▪️ Токен: <code>{self.token}</code>
                ▪️ Лимиты: <code>{text_limit}</code>
                ▪️ Идентификация: <code>{text_identification}</code>
                ▪️ СМС оповещения: <code>{text_notification}</code>
                ▪️ Почта: <code>{response['authInfo']['boundEmail']}</code>
                ▪️ Регистрация аккаунта: <code>{response['authInfo']['registrationDate']}</code>
            """)
        else:
            if code == 400:
                return_message = "Номер телефона указан в неверном формате"
            elif code == 401:
                return_message = "Неверный токен или истек срок действия токена API"
            elif code == 403:
                return_message = "Нет прав на данный запрос (недостаточно разрешений у токена API)"
            elif code == "CERTIFICATE_VERIFY_FAILED":
                return_message = ded(f"""
                    CERTIFICATE_VERIFY_FAILED certificate verify failed: self signed certificate in certificate chain
                    Ваш сервер/дедик/устройство блокируют запросы к QIWI. Отключите антивирус или другие блокирующие ПО.
                """)
            else:
                return_message = code

        return_message = ded(f"""
            <b>🥝 QIWI данные не прошли проверку ❌</b>
            ▶️ Код ошибки: <code>{return_message}</code>
        """)

        return False, return_message

    # Изменение аккаунта
    async def edit(self) -> tuple[bool, str]:
        status, response = await self.check()

        if status:
            status_limit = await self.check_limits()

            if status_limit:
                text_limit = "❗️ На аккаунте имеются ограничения"
            else:
                text_limit = "❕️ Аккаунт не имеет никаких ограничений"

            return True, ded(f"""
                <b>🥝 QIWI кошелёк был успешно изменён ✅</b>
                {text_limit}
            """)
        else:
            return False, ""

    # Генерация платежа
    async def bill(self, pay_amount: float) -> tuple[str, str, int]:
        bill_receipt = gen_id()

        bill_url = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={self.login}&amountInteger={pay_amount}&amountFraction=0&extra%5B%27comment%27%5D={bill_receipt}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

        bill_message = ded(f"""
            <b>💰 Пополнение баланса</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Для пополнения баланса, нажмите на кнопку ниже 
            <code>Перейти к оплате</code> и оплатите выставленный вам счёт
            ▪️ QIWI кошелёк: <code>{self.login}</code>
            ▪️ Комментарий: <code>{bill_receipt}</code>
            ▪️ Сумма пополнения: <code>{pay_amount}₽</code>
            ➖➖➖➖➖➖➖➖➖➖
            ❗️ После оплаты, нажмите на <code>Проверить оплату</code>
        """)

        return bill_message, bill_url, bill_receipt

    # Проверка платежа
    async def bill_check(self, receipt: Union[str, int]) -> tuple[int, float]:
        url = f"https://edge.qiwi.com/payment-history/v2/persons/{self.login[1:]}/payments"

        parameters = {
            'rows': 50,
        }

        status, response, code = await self._request("GET", url, parameters)

        pay_status = 1
        pay_amount = 0

        if status:
            pay_status = 2

            for check_pay in response['data']:
                if str(receipt) == str(check_pay['comment']):
                    if "643" == str(check_pay['sum']['currency']):
                        pay_amount = int(float(check_pay['sum']['amount']))
                        pay_status = 0
                    else:
                        pay_status = 3

                    break

        return pay_status, pay_amount

    # Генерация запроса
    async def _request(
            self,
            method: str,
            url: str,
            params: dict = None,
    ) -> tuple[bool, any, int]:
        session = await self.arSession.get_session()

        try:
            response = await session.get(url, params=params, headers=self.headers, ssl=False)
            response_data = json.loads((await response.read()).decode())

            if response.status == 200:
                return True, response_data, 200
            else:
                await self.error_wallet_user()
                await self.error_wallet_admin(f"{response.status} - {str(response_data)}")

                return False, response_data, response.status
        except ClientConnectorCertificateError:
            await self.error_wallet_user()
            await self.error_wallet_admin("CERTIFICATE_VERIFY_FAILED")

            return False, "CERTIFICATE_VERIFY_FAILED", response.status
        except Exception as ex:
            await self.error_wallet_user()
            await self.error_wallet_admin(str(ex))

            return False, str(ex), response.status
