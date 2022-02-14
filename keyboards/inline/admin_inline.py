# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Рассылка
sure_send_ad_inl = InlineKeyboardMarkup()
yes_send_kb = InlineKeyboardButton(text="✅ Отправить", callback_data="yes_send_ad")
not_send_kb = InlineKeyboardButton(text="❌ Отменить", callback_data="not_send_kb")
sure_send_ad_inl.add(yes_send_kb, not_send_kb)

# Удаление категорий
confirm_clear_category_inl = InlineKeyboardMarkup()
yes_clear_cat_kb = InlineKeyboardButton(text="❌ Да, удалить все", callback_data="confirm_clear_category")
not_clear_cat_kb = InlineKeyboardButton(text="✅ Нет, отменить", callback_data="cancel_clear_category")
confirm_clear_category_inl.add(yes_clear_cat_kb, not_clear_cat_kb)

# Удаление позиций
confirm_clear_position_inl = InlineKeyboardMarkup()
yes_clear_cat_kb = InlineKeyboardButton(text="❌ Да, удалить все", callback_data="confirm_clear_position")
not_clear_cat_kb = InlineKeyboardButton(text="✅ Нет, отменить", callback_data="cancel_clear_position")
confirm_clear_position_inl.add(yes_clear_cat_kb, not_clear_cat_kb)

# Удаление товаров
confirm_clear_item_inl = InlineKeyboardMarkup()
yes_clear_item_kb = InlineKeyboardButton(text="❌ Да, удалить все", callback_data="confirm_clear_item")
not_clear_item_kb = InlineKeyboardButton(text="✅ Нет, отменить", callback_data="cancel_clear_item")
confirm_clear_item_inl.add(yes_clear_item_kb, not_clear_item_kb)

# Удаление товара
delete_item_inl = InlineKeyboardMarkup()
delete_item_inl.add(InlineKeyboardButton(text="🎁 Удалить товар", callback_data="delete_this_item"))
