# - *- coding: utf- 8 - *-
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import CantParseEntities

from filters import IsAdmin
from keyboards.default import get_settings_func
from loader import dp
from states import StorageSettings
from utils.db_api.sqlite import *
from utils.other_func import send_all_admin, clear_firstname


# Обработка кнопки "Изменить Faq"
@dp.message_handler(IsAdmin(), text="ℹ Изменить FAQ 🖍", state="*")
async def change_faq(message: types.Message, state: FSMContext):
    await state.finish()
    get_faq = get_settingsx()
    await message.answer(f"<b>ℹ Текущее FAQ:</b>\n{get_faq[1]}")
    await message.answer("<b>🖍 Введите новый текст для FAQ</b>\n"
                         "❕ Вы можете использовать заготовленный синтаксис и HTML разметку:\n"
                         "▶ <code>{username}</code>  - логин пользоваля\n"
                         "▶ <code>{user_id}</code>   - айди пользовател\n"
                         "▶ <code>{firstname}</code> - имя пользователя")
    await StorageSettings.here_faq.set()


# Обработка кнопки "Изменить контакты"
@dp.message_handler(IsAdmin(), text="📕 Изменить контакты 🖍", state="*")
async def change_contact(message: types.Message, state: FSMContext):
    await state.finish()
    get_contact = get_settingsx()
    await message.answer(f"<b>📕 Текущие контакты:</b>\n{get_contact[0]}")
    await message.answer("🖍 Отправьте ID пользователя.\n"
                         "❕ Вводимый ID должен быть пользователем бота.")
    await StorageSettings.here_contact.set()


# Выключение покупок
@dp.message_handler(IsAdmin(), text="🔴 Выключить покупки", state="*")
async def turn_off_buy(message: types.Message, state: FSMContext):
    await state.finish()
    update_settingsx(status_buy="False")
    await message.answer("<b>🔴 Покупки в боте были выключены.</b>",
                         reply_markup=get_settings_func())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🔴 Выключил покупки в боте.", not_me=message.from_user.id)


# Включение покупок
@dp.message_handler(IsAdmin(), text="🟢 Включить покупки", state="*")
async def turn_on_buy(message: types.Message, state: FSMContext):
    await state.finish()
    update_settingsx(status_buy="True")
    await message.answer("<b>🟢 Покупки в боте были включены.</b>",
                         reply_markup=get_settings_func())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🟢 Включил покупки в боте.", not_me=message.from_user.id)


# Обработка кнопки "Отправить бота на тех. работы"
@dp.message_handler(IsAdmin(), text="🔴 Отправить на тех. работы", state="*")
async def send_bot_to_work(message: types.Message, state: FSMContext):
    await state.finish()
    update_settingsx(status="False")
    await message.answer("<b>🔴 Бот был отправлен на технические работы.</b>",
                         reply_markup=get_settings_func())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🔴 Отправил бота на технические работы.", not_me=message.from_user.id)


# Обработка кнопки "Вывести бота из тех. работ"
@dp.message_handler(IsAdmin(), text="🟢 Вывести из тех. работ", state="*")
async def return_bot_from_work(message: types.Message, state: FSMContext):
    await state.finish()
    update_settingsx(status="True")
    await message.answer("<b>🟢 Бот был выведен из технических работ.</b>",
                         reply_markup=get_settings_func())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🟢 Вывел бота из технических работ.", not_me=message.from_user.id)


# Принятие нового текста для faq
@dp.message_handler(IsAdmin(), state=StorageSettings.here_faq)
async def get_text_for_change_faq(message: types.Message, state: FSMContext):
    send_msg = message.text
    msg = message.text
    if "{username}" in msg:
        msg = msg.replace("{username}", f"<b>{message.from_user.username}</b>")
    if "{user_id}" in msg:
        msg = msg.replace("{user_id}", f"<b>{message.from_user.id}</b>")
    if "{firstname}" in msg:
        msg = msg.replace("{firstname}", f"<b>{clear_firstname(message.from_user.first_name)}</b>")
    try:
        await state.finish()
        await message.answer(f"ℹ FAQ был обновлён ✅ Пример:\n{msg}",
                             reply_markup=get_settings_func())
        update_settingsx(faq=send_msg)
    except CantParseEntities:
        await StorageSettings.here_faq.set()
        await message.answer("<b>❌ Ошибка синтаксиса HTML.</b>\n"
                             "🖍 Введите новый текст для FAQ")


# Принятие нового айди для контактов
@dp.message_handler(IsAdmin(), state=StorageSettings.here_contact)
async def get_id_for_change_contact(message: types.Message, state: FSMContext):
    msg = message.text
    if msg.isdigit():
        get_status_user = get_userx(user_id=msg)
        if get_status_user is None:
            await StorageSettings.here_contact.set()
            await message.answer("<b>❌ Пользователь не был найден.</b>\n🖍 Отправьте ID пользователя.")
        else:
            await state.finish()
            msg = f"📕 <b>Писать сюда ➡ <a href='tg://user?id={msg}'>Администратор</a></b>"
            update_settingsx(contact=msg)
            await message.answer(f"📕 Контакты были успешно обновлены ✅",
                                 reply_markup=get_settings_func())
    else:
        await StorageSettings.here_contact.set()
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "🖍 Отправьте ID пользователя.")
