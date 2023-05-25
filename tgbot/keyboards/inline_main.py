# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as ikb

# Рассылка
mail_confirm_inl = InlineKeyboardMarkup(
).add(
    ikb("✅ Отправить", callback_data="confirm_mail:yes"),
    ikb("❌ Отменить", callback_data="confirm_mail:not")
)

# Кнопки при поиске профиля через админ-меню
profile_open_inl = InlineKeyboardMarkup(
).add(
    ikb("💰 Пополнить", callback_data="user_refill"),
    ikb("🎁 Мои покупки", callback_data="user_history")
)

# Удаление сообщения
close_inl = InlineKeyboardMarkup(
).add(
    ikb("❌ Закрыть", callback_data="close_this"),
)

######################################## ТОВАРЫ ########################################
# Удаление категорий
category_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    ikb("❌ Да, удалить все", callback_data="confirm_remove_category:yes"),
    ikb("✅ Нет, отменить", callback_data="confirm_remove_category:not")
)

# Удаление позиций
position_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    ikb("❌ Да, удалить все", callback_data="confirm_remove_position:yes"),
    ikb("✅ Нет, отменить", callback_data="confirm_remove_position:not")
)

# Удаление товаров
item_remove_confirm_inl = InlineKeyboardMarkup(
).add(
    ikb("❌ Да, удалить все", callback_data="confirm_remove_item:yes"),
    ikb("✅ Нет, отменить", callback_data="confirm_remove_item:not")
)
