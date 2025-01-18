# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from tgbot.data.config import get_admins
from tgbot.utils.const_functions import rkb, ikb


# Кнопки главного меню
def menu_frep(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🎁 Купить", data="inline_buy")
    ).row(
        ikb("👤 Профиль", data="inline_profile")
    ).row(
        ikb("🧮 Наличие товаров", data="inline_product_availability")
    ).row(
        ikb("☎️ Поддержка", data="inline_support")
    ).row(
        ikb("❔ FAQ", data="inline_faq")
    )

    if user_id in get_admins():
        keyboard.row(
            ikb("🎁 Управление товарами", data="inline_goods_management")
        ).row(
            ikb("📊 Статистика", data="inline_stats")
        ).row(
            ikb("🔆 Общие функции", data="inline_general_functions")
        ).row(
            ikb("🔑 Платежные системы", data="inline_payment_systems")
        ).row(
            ikb("⚙️ Настройки", data="inline_settings")
        )

    return keyboard.as_markup()


# Кнопки платежных систем
def payments_frep() -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("₿ Cryptocloud", data="inline_payment_cryptocloud"), 
    ).row(
        ikb("🔷 CryptoBot", data="inline_payment_cryptobot"), 
    ).row(
        ikb("🔮 ЮMoney", data="inline_payment_yoomoney"),
    ).row(
        ikb("🔙 Главное меню", data="inline_main_menu"),
    )

    return keyboard.as_markup()


# Кнопки общих функций
def functions_frep() -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🔍 Поиск", data="inline_search"), ikb("📢 Рассылка", data="inline_mass_dm"),
    ).row(
        ikb("🔙 Главное меню", data="inline_main_menu"),
    )

    return keyboard.as_markup()


# Кнопки настроек
def settings_frep() -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🖍 Изменить данные", data="inline_change_data"), ikb("🕹 Выключатели", data="inline_enablers"),
    ).row(
        ikb("🔙 Главное меню", data="inline_main_menu"),
    )

    return keyboard.as_markup()


# Кнопки изменения товаров
def items_frep() -> ReplyKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("📁 Создать позицию ➕", data="inline_create_position"), ikb("🗃 Создать категорию ➕", data="inline_create_category"),
    ).row(
        ikb("📁 Изменить позицию 🖍", data="inline_change_position"), ikb("🗃 Изменить категорию 🖍", data="inline_change_category"),
    ).row(
        ikb("🔙 Главное меню", data="inline_main_menu"), ikb("🎁 Добавить товары ➕", data="inline_add_goods"), ikb("❌ Удаление", data="inline_delete_items"),
    )

    return keyboard.as_markup()
