# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup

items_default = ReplyKeyboardMarkup(resize_keyboard=True)
items_default.row("🎁 Добавить товары ➕", "🎁 Изменить товары 🖍", "🎁 Удалить товары ❌")
items_default.row("📁 Создать позицию ➕", "📁 Изменить позицию 🖍", "📁 Удалить позиции ❌")
items_default.row("📜 Создать категорию ➕", "📜 Изменить категорию 🖍", "📜 Удалить категории ❌")
items_default.row("⬅ На главную")

skip_send_image_default = ReplyKeyboardMarkup(resize_keyboard=True)
skip_send_image_default.row("📸 Пропустить")

cancel_send_image_default = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_send_image_default.row("📸 Отменить")

finish_load_items_default = ReplyKeyboardMarkup(resize_keyboard=True)
finish_load_items_default.row("📥 Закончить загрузку товаров")
