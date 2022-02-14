# - *- coding: utf- 8 - *-
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageCantBeDeleted

from keyboards.default import check_user_out_func
from loader import dp


# Обработка всех колбэков которые потеряли стейты после перезапуска скрипта
@dp.callback_query_handler(text="...", state="*")
async def processing_missed_callback(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)


# Обработка всех колбэков которые потеряли стейты после перезапуска скрипта
@dp.callback_query_handler(state="*")
async def processing_missed_callback(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except MessageCantBeDeleted:
        pass
    await call.message.answer("<b>❌ Данные не были найдены из-за перезапуска скрипта.\n"
                              "♻ Выполните действие заново.</b>",
                              reply_markup=check_user_out_func(call.from_user.id))


# Обработка всех неизвестных сообщений
@dp.message_handler()
async def processing_missed_messages(message: types.Message):
    await message.answer("<b>♦ Неизвестная команда.</b>\n"
                         "▶ Введите /start")
