# - *- coding: utf- 8 - *-
from typing import Union

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.utils.const_functions import ikb


################################### КАТЕГОРИИ ##################################
# Изменение категории
def category_edit_open_finl(category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("▪️ Изм. Название", data=f"category_edit_name:{category_id}:{remover}"),
        ikb("▪️ Добавить позицию", data=f"position_add_open:{category_id}"),
    ).row(
        ikb("🔙 Вернуться", data=f"catategory_edit_swipe:{remover}"),
        ikb("▪️ Удалить", data=f"category_edit_delete:{category_id}:{remover}")
    )

    return keyboard.as_markup()


# Подтверждение удаления категории
def category_edit_delete_finl(category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Да, удалить", data=f"category_edit_delete_confirm:{category_id}:{remover}"),
        ikb("❌ Нет, отменить", data=f"category_edit_open:{category_id}:{remover}")
    )

    return keyboard.as_markup()


# Отмена изменения категории и возвращение
def category_edit_cancel_finl(category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("❌ Отменить", data=f"category_edit_open:{category_id}:{remover}"),
    )

    return keyboard.as_markup()


#################################### ПОЗИЦИИ ###################################
# Кнопки при открытии позиции для изменения
def position_edit_open_finl(position_id, category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("▪️ Изм. Название", data=f"position_edit_name:{position_id}:{category_id}:{remover}"),
        ikb("▪️ Изм. цену", data=f"position_edit_price:{position_id}:{category_id}:{remover}"),
    ).row(
        ikb("▪️ Изм. Описание", data=f"position_edit_desc:{position_id}:{category_id}:{remover}"),
        ikb("▪️ Изм. Фото", data=f"position_edit_photo:{position_id}:{category_id}:{remover}"),
    ).row(
        ikb("▪️ Добавить Товары", data=f"item_add_position_open:{position_id}:{category_id}"),
        ikb("▪️ Выгрузить Товары", data=f"position_edit_items:{position_id}:{category_id}:{remover}"),
    ).row(
        ikb("▪️ Очистить Товары", data=f"position_edit_clear:{position_id}:{category_id}:{remover}"),
        ikb("▪️ Удалить Товар", data=f"item_delete_swipe:{position_id}:{category_id}:0"),
    ).row(
        ikb("▪️ Удалить Позицию", data=f"position_edit_delete:{position_id}:{category_id}:{remover}"),
    ).row(
        ikb("🔙 Вернуться", data=f"position_edit_swipe:{category_id}:{remover}"),
        ikb("▪️ Обновить", data=f"position_edit_open:{position_id}:{category_id}:{remover}"),
    )

    return keyboard.as_markup()


# Подтверждение удаления позиции
def position_edit_delete_finl(position_id, category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Да, удалить", data=f"position_edit_delete_confirm:{position_id}:{category_id}:{remover}"),
        ikb("❌ Нет, отменить", data=f"position_edit_open:{position_id}:{category_id}:{remover}")
    )

    return keyboard.as_markup()


# Подтверждение очистики позиции
def position_edit_clear_finl(position_id, category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Да, очистить", data=f"position_edit_clear_confirm:{position_id}:{category_id}:{remover}"),
        ikb("❌ Нет, отменить", data=f"position_edit_open:{position_id}:{category_id}:{remover}")
    )

    return keyboard.as_markup()


# Отмена изменения позиции и возвращение
def position_edit_cancel_finl(position_id, category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("❌ Отменить", data=f"position_edit_open:{position_id}:{category_id}:{remover}"),
    )

    return keyboard.as_markup()


##################################### ТОВАРЫ ###################################
# Отмена изменения позиции и возвращение
def item_add_finish_finl(position_id: Union[int, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Завершить загрузку", data=f"item_add_position_finish:{position_id}"),
    )

    return keyboard.as_markup()


# Удаление товара
def item_delete_finl(item_id, position_id, category_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("▪️ Удалить товар", data=f"item_delete_confirm:{item_id}"),
    ).row(
        ikb("🔙 Вернуться", data=f"item_delete_swipe:{position_id}:{category_id}:0"),
    )

    return keyboard.as_markup()


############################### УДАЛЕНИЕ РАЗДЕЛОВ ##############################
# Выбор раздела для удаления
def products_removes_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🗃 Удалить все категории", data=f"prod_removes_categories"),
    ).row(
        ikb("📁 Удалить все позиции", data=f"prod_removes_positions"),
    ).row(
        ikb("🎁 Удалить все товары", data=f"prod_removes_items"),
    )

    return keyboard.as_markup()


# Удаление всех категорий
def products_removes_categories_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Да, удалить все", data="prod_removes_categories_confirm"),
        ikb("❌ Нет, отменить", data="prod_removes_return")
    )

    return keyboard.as_markup()


# Удаление всех позиций
def products_removes_positions_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Да, удалить все", data="prod_removes_positions_confirm"),
        ikb("❌ Нет, отменить", data="prod_removes_return")
    )

    return keyboard.as_markup()


# Удаление всех товаров
def products_removes_items_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Да, удалить все", data="prod_removes_items_confirm"),
        ikb("❌ Нет, отменить", data="prod_removes_return")
    )

    return keyboard.as_markup()
