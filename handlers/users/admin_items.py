# - *- coding: utf- 8 - *-

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import CantParseEntities

from filters import IsAdmin
from keyboards.default import items_default, skip_send_image_default, cancel_send_image_default, \
    finish_load_items_default
from keyboards.inline import *
from keyboards.inline.inline_page import *
from loader import dp, bot
from middlewares.throttling import rate_limit
from states.state_items import StoragePosition, StorageCategory, StorageItems
from utils.other_func import clear_firstname, get_dates


# Создание новой категории
@dp.message_handler(IsAdmin(), text="📜 Создать категорию ➕", state="*")
async def category_create_new(message: types.Message, state: FSMContext):
    await state.finish()
    await StorageCategory.here_input_category_name.set()
    await message.answer("<b>📜 Введите название для категории 🏷</b>")


# Открытие страниц выбора категорий для редактирования
@dp.message_handler(IsAdmin(), text="📜 Изменить категорию 🖍", state="*")
async def category_open_edit(message: types.Message, state: FSMContext):
    await state.finish()
    get_categories = get_all_categoriesx()
    if len(get_categories) >= 1:
        get_kb = category_open_edit_ap(0)
        await message.answer("<b>📜 Выберите категорию для изменения 🖍</b>", reply_markup=get_kb)
    else:
        await message.answer("<b>📜 Категории отсутствуют 🖍</b>")


# Окно с уточнением удалить все категории (позиции и товары включительно)
@dp.message_handler(IsAdmin(), text="📜 Удалить категории ❌", state="*")
async def category_remove_all(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>📜 Вы действительно хотите удалить все категории? ❌</b>\n"
                         "❗ Так же будут удалены все позиции и товары",
                         reply_markup=confirm_clear_category_inl)


# Создание новой позиции
@dp.message_handler(IsAdmin(), text="📁 Создать позицию ➕", state="*")
async def position_create_new(message: types.Message, state: FSMContext):
    await state.finish()
    get_categories = get_all_categoriesx()
    if len(get_categories) >= 1:
        get_kb = position_open_create_ap(0)
        await message.answer("<b>📁 Выберите место для позиции ➕</b>", reply_markup=get_kb)
    else:
        await message.answer("<b>❌ Отсутствуют категории для создания позиции.</b>")


# Начальные категории для изменения позиции
@dp.message_handler(IsAdmin(), text="📁 Изменить позицию 🖍", state="*")
async def choice_category_for_edit_position(message: types.Message, state: FSMContext):
    await state.finish()
    get_kb = position_open_edit_category_ap(0)
    await message.answer("<b>📁 Выберите категорию с нужной вам позицией 🖍</b>", reply_markup=get_kb)


# Подтверждение удаления всех позиций
@dp.message_handler(IsAdmin(), text="📁 Удалить позиции ❌", state="*")
async def open_create_position(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>📜 Вы действительно хотите удалить все позиции? ❌</b>\n"
                         "❗ Так же будут удалены все товары",
                         reply_markup=confirm_clear_position_inl)


# Начальные категории для добавления товаров
@dp.message_handler(IsAdmin(), text="🎁 Добавить товары ➕", state="*")
async def choice_category_for_edit_position(message: types.Message, state: FSMContext):
    await state.finish()
    get_positions = get_all_positionsx()
    if len(get_positions) >= 1:
        get_kb = item_open_add_category_ap(0)
        await message.answer("<b>🎁 Выберите категорию с нужной вам позицией ➕</b>", reply_markup=get_kb)
    else:
        await message.answer("<b>❌ Отсутствуют позиции для добавления товара.</b>")


# Кнопка с изменением товаров
@dp.message_handler(IsAdmin(), text="🎁 Изменить товары 🖍", state="*")
async def open_edit_items(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>🔹 Получение всех товаров и их позиций:</b> /getinfoitems\n"
                         "<b>🔸 Получение всех позиций:</b> /getposition\n"
                         "<b>🔹 Получение всех товаров:</b> /getitems\n"
                         "<b>🔸 Получение базы данных:</b> /getbd",
                         reply_markup=delete_item_inl)


# Кнопки с подтверждением удаления всех категорий
@dp.message_handler(IsAdmin(), text="🎁 Удалить товары ❌", state="*")
async def open_create_category(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>🎁 Вы действительно хотите удалить все товары?</b> ❌\n",
                         reply_markup=confirm_clear_item_inl)


################################################################################################
####################################### СОЗДАНИЕ КАТЕГОРИЙ #####################################
# Принятие названия категории для её создания
@dp.message_handler(IsAdmin(), state=StorageCategory.here_input_category_name)
async def category_create_input_name(message: types.Message, state: FSMContext):
    category_id = [random.randint(100000000, 999999999)]
    add_categoryx(category_id[0], message.text)
    await state.finish()
    await message.answer("<b>📜 Категория была успешно создана ✅</b>",
                         reply_markup=items_default)


################################################################################################
####################################### ИЗМЕНЕНИЕ КАТЕГОРИЙ ####################################
# Сделующая страница выбора категорий для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_catategory_nextp", state="*")
async def category_edit_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = category_edit_next_page_ap(remover)
    await bot.edit_message_text("<b>📜 Выберите категорию для изменения 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Предыдущая страница выбора категорий для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_catategory_prevp", state="*")
async def category_edit_prev_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = category_edit_prev_page_ap(remover)
    await bot.edit_message_text("<b>📜 Выберите категорию для изменения 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Выбор текущей категории для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_category_here", state="*")
async def category_open_for_edit(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    messages, keyboard = edit_category_func(category_id, remover)
    await bot.edit_message_text(messages,
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=keyboard)


# Возвращение к списку выбора категорий для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="back_category_edit", state="*")
async def category_back_for_edit(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = category_open_edit_ap(remover)
    await bot.edit_message_text("<b>📜 Выберите категорию для изменения 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


######################################## САМО ИЗМЕНЕНИЕ КАТЕГОРИИ ########################################
# Изменение названия категории
@dp.callback_query_handler(IsAdmin(), text_startswith="category_edit_name", state="*")
async def category_edit_name(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    async with state.proxy() as data:
        data["here_cache_category_id"] = category_id
        data["here_cache_category_remover"] = remover
    await StorageCategory.here_change_category_name.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>🏷 Введите новое название для категории:</b>")


# Принятие нового имени для категории
@dp.message_handler(IsAdmin(), state=StorageCategory.here_change_category_name)
async def category_name_was_changed(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        category_id = data["here_cache_category_id"]
        remover = data["here_cache_category_remover"]
    update_categoryx(category_id, category_name=message.text)
    await state.finish()
    await message.answer("<b>📜 Название было успешно изменено ✅</b>",
                         reply_markup=items_default)
    messages, keyboard = edit_category_func(category_id, remover)
    await message.answer(messages, reply_markup=keyboard)


# Окно с уточнением удалить категорию
@dp.callback_query_handler(IsAdmin(), text_startswith="category_remove", state="*")
async def category_remove(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    await bot.edit_message_text("<b>❗ Вы действительно хотите удалить категорию и все её данные?</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=confirm_remove_func(category_id, remover))


# Отмена удаления категории
@dp.callback_query_handler(IsAdmin(), text_startswith="not_remove_category", state="*")
async def category_remove_cancel(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    messages, keyboard = edit_category_func(category_id, remover)
    await bot.edit_message_text(messages,
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=keyboard)


# Согласие на удаление категории
@dp.callback_query_handler(IsAdmin(), text_startswith="yes_remove_category", state="*")
async def category_remove_confirm(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    remove_categoryx(category_id=category_id)  # Удаление всех категорий
    remove_positionx(category_id=category_id)  # Удаление всех позиций
    remove_itemx(category_id=category_id)  # Удаление всех товаров

    await bot.edit_message_text("<b>📜 Категория и все её данные были успешно удалены ✅</b>",
                                call.from_user.id,
                                call.message.message_id)
    get_kb = category_open_edit_ap(remover)
    await bot.send_message(call.from_user.id,
                           "<b>📜 Выберите категорию для изменения 🖍</b>",
                           reply_markup=get_kb)


################################################################################################
#################################### УДАЛЕНИЕ ВСЕХ КАТЕГОРИЙ ###################################
# Согласие на удаление всех категорий (позиций и товаров включительно)
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_clear_category", state="*")
async def category_remove_all_confirm(call: CallbackQuery, state: FSMContext):
    clear_categoryx()
    clear_positionx()
    clear_itemx()
    await bot.edit_message_text("<b>☑ Вы успешно удалили все категории, позиции и товары</b>",
                                call.from_user.id,
                                call.message.message_id)


# Отмена удаления всех категорий (позиций и товаров включительно)
@dp.callback_query_handler(IsAdmin(), text_startswith="cancel_clear_category", state="*")
async def category_remove_all_cancel(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text("<b>☑ Вы отменили удаление всех категорий ☑</b>",
                                call.from_user.id,
                                call.message.message_id)


################################################################################################
####################################### ДОБАВЛЕНИЕ ПОЗИЦИЙ #####################################
# Сделующая страница выбора категорий для создания позиций
@dp.callback_query_handler(IsAdmin(), text_startswith="create_position_nextp", state="*")
async def position_next_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = position_create_next_page_ap(remover)
    await bot.edit_message_text("<b>📁 Выберите место для позиции ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Предыдущая страница выбора категорий для создания позиций
@dp.callback_query_handler(IsAdmin(), text_startswith="create_position_prevp", state="*")
async def position_prev_page(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = position_create_previous_page_ap(remover)
    await bot.edit_message_text("<b>📁 Выберите место для позиции ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Выбор категории для создания позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="create_position_here", state="*")
async def position_select_category_for_create(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    async with state.proxy() as data:
        data["here_cache_change_category_id"] = category_id
    await StoragePosition.here_input_position_name.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>📁 Введите название для позиции 🏷</b>")


# Принятие имени для создания позиции
@dp.message_handler(IsAdmin(), state=StoragePosition.here_input_position_name)
async def position_input_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_position_name"] = message.text
    await StoragePosition.here_input_position_price.set()
    await message.answer("<b>📁 Введите цену для позиции 💰</b>")


# Принятие цены позиции для её создания
@dp.message_handler(IsAdmin(), state=StoragePosition.here_input_position_price)
async def position_input_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 0:
            async with state.proxy() as data:
                data["here_input_position_price"] = message.text
            await StoragePosition.here_input_position_discription.set()
            await message.answer("<b>📁 Введите описание для позиции 📜</b>\n"
                                 "❕ Вы можете использовать HTML разметку")
        else:
            await StoragePosition.here_input_position_price.set()
            await message.answer("<b>❌ Минимальная цена для позиции 0 рублей.</b>\n"
                                 "📁 Введите цену для позиции 💰")
    else:
        await StoragePosition.here_input_position_price.set()
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "📁 Введите цену для позиции 💰")


# Принятие описания позиции для её создания
@dp.message_handler(IsAdmin(), state=StoragePosition.here_input_position_discription)
async def position_input_discription(message: types.Message, state: FSMContext):
    try:
        delete_msg = await message.answer(message.text)
        await bot.delete_message(message.chat.id, delete_msg.message_id)
        async with state.proxy() as data:
            data["here_input_position_discription"] = message.text
        await StoragePosition.here_input_position_image.set()
        await message.answer("<b>📁 Отправьте изображение для позиции 📸</b>", reply_markup=skip_send_image_default)
    except CantParseEntities:
        await StoragePosition.here_input_position_discription.set()
        await bot.send_message(message.from_user.id,
                               "<b>❌ Ошибка синтаксиса HTML.</b>\n"
                               "📁 Введите описание для позиции 📜\n"
                               "❕ Вы можете использовать HTML разметку")


# Принятие пропуска изображения позиции для её создания
@dp.message_handler(IsAdmin(), text="📸 Пропустить", state=StoragePosition.here_input_position_image)
async def position_skip_get_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_name = data["here_input_position_name"]
        position_price = data["here_input_position_price"]
        position_discription = data["here_input_position_discription"]
        catategory_id = data["here_cache_change_category_id"]
    await state.finish()
    position_id = [random.randint(100000000, 999999999)]
    add_positionx(position_id[0], position_name, position_price, position_discription,
                  "", get_dates(), catategory_id)
    await message.answer("<b>📁 Позиция была успешно создана ✅</b>",
                         reply_markup=items_default)


# Принятие изображения позиции для её создания
@dp.message_handler(content_types=["photo"], state=StoragePosition.here_input_position_image)
async def position_get_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_name = data["here_input_position_name"]
        position_price = data["here_input_position_price"]
        position_discription = data["here_input_position_discription"]
        catategory_id = data["here_cache_change_category_id"]
    position_photo = message.photo[0].file_id
    await state.finish()
    position_id = [random.randint(100000000, 999999999)]
    add_positionx(position_id[0], position_name, position_price, position_discription,
                  position_photo, get_dates(), catategory_id)
    await message.answer("<b>📁 Позиция была успешно создана ✅</b>",
                         reply_markup=items_default)


################################################################################################
####################################### ИЗМЕНЕНИЕ ПОЗИЦИЙ #####################################
# Возвращение к начальным категориям для изменения позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="back_to_category", state="*")
async def back_to_all_categories_for_edit_position(call: CallbackQuery, state: FSMContext):
    get_kb = position_open_edit_category_ap(0)

    await bot.edit_message_text("<b>📁 Выберите категорию с нужной вам позицией 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Сделующая страница выбора категории с позицией для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_position_category_nextp", state="*")
async def next_page_category_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = position_edit_next_page_category_ap(remover)
    await bot.edit_message_text("<b>📁 Выберите категорию с нужной вам позицией 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Предыдущая страница выбора категории с позицией для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_position_category_prevp", state="*")
async def previous_page_category_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = position_edit_previous_page_category_ap(remover)
    await bot.edit_message_text("<b>📁 Выберите категорию с нужной вам позицией 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Выбор категории с нужной позицией
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit_category", state="*")
async def open_category_for_edit_position(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])

    get_positions = get_positionsx("*", category_id=category_id)
    if len(get_positions) >= 1:
        get_kb = position_open_edit_ap(0, category_id)
        await bot.edit_message_text("<b>📁 Выберите нужную вам позицию 🖍</b>",
                                    call.from_user.id,
                                    call.message.message_id,
                                    reply_markup=get_kb)
    else:
        await bot.answer_callback_query(call.id, "📁 Позиции в данной категории отсутствуют")


# Сделующая страница позиций для их изменения
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_position_nextp", state="*")
async def next_page_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    get_kb = position_edit_next_page_ap(remover, category_id)
    await bot.edit_message_text("<b>📁 Выберите категорию с нужной вам позицией 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Предыдущая страница позиций для их изменения
@dp.callback_query_handler(IsAdmin(), text_startswith="edit_position_prevp", state="*")
async def previous_page_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    get_kb = position_edit_previous_page_ap(remover, category_id)
    await bot.edit_message_text("<b>📁 Выберите категорию с нужной вам позицией 🖍</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Выбор позиции для редактирования
@dp.callback_query_handler(IsAdmin(), text_startswith="position_edit", state="*")
async def open_for_edit_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    category_id = int(call.data.split(":")[3])
    get_position = get_positionx("*", position_id=position_id)
    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)

    if have_photo:
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_photo(call.from_user.id, get_position[5], messages, reply_markup=keyboard)
    else:
        await bot.edit_message_text(messages,
                                    call.from_user.id,
                                    call.message.message_id,
                                    reply_markup=keyboard)


# Возвращение к выбору позиции для изменения
@dp.callback_query_handler(IsAdmin(), text_startswith="back_position_edit", state="*")
async def back_to_all_categories_for_choice_edit(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_positions = get_positionsx("*", category_id=category_id)
    if len(get_positions) >= 1:
        get_kb = position_open_edit_ap(remover, category_id)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id,
                               "<b>📁 Выберите нужную вам позицию 🖍</b>",
                               reply_markup=get_kb)
    else:
        await bot.edit_message_text("<b>❗ Позиции в данной категории отсутствуют</b>",
                                    call.from_user.id,
                                    call.message.message_id)


######################################## САМО ИЗМЕНЕНИЕ ПОЗИЦИИ ########################################
# Изменение имени позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_change_name", state="*")
async def change_position_name(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])
    async with state.proxy() as data:
        data["here_cache_category_id"] = category_id
        data["here_cache_position_id"] = position_id
        data["here_cache_position_remover"] = remover
    await StoragePosition.here_change_position_name.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>🏷 Введите новое название для позиции</b>")


# Принятие имени позиции для её изменения
@dp.message_handler(IsAdmin(), state=StoragePosition.here_change_position_name)
async def input_new_position_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data["here_cache_category_id"]
        category_id = data["here_cache_position_id"]
        remover = data["here_cache_position_remover"]
    update_positionx(position_id, position_name=message.text)

    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
    await message.answer("<b>✅ Название позиции было успешно изменено</b>", reply_markup=items_default)
    await state.finish()

    get_position = get_positionx("*", position_id=position_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    if have_photo:
        await message.answer_photo(get_position[5], messages, reply_markup=keyboard)
    else:
        await message.answer(messages, reply_markup=keyboard)


# Изменение цены позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_change_price", state="*")
async def change_position_price(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])
    async with state.proxy() as data:
        data["here_cache_category_id"] = category_id
        data["here_cache_position_id"] = position_id
        data["here_cache_position_remover"] = remover
    await StoragePosition.here_change_position_price.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>💰 Введите новую цену для позиции</b>")


# Принятие цены позиции для её изменения
@dp.message_handler(IsAdmin(), state=StoragePosition.here_change_position_price)
async def input_new_position_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) >= 0:
            async with state.proxy() as data:
                position_id = data["here_cache_category_id"]
                category_id = data["here_cache_position_id"]
                remover = data["here_cache_position_remover"]
            update_positionx(position_id, position_price=message.text)

            messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
            await message.answer("<b>✅ Цена позиции была успешно изменена</b>", reply_markup=items_default)
            await state.finish()

            get_position = get_positionx("*", position_id=position_id)
            await bot.delete_message(message.from_user.id, message.message_id)
            if have_photo:
                await message.answer_photo(get_position[5], messages, reply_markup=keyboard)
            else:
                await message.answer(messages, reply_markup=keyboard)
        else:
            await StoragePosition.here_change_position_name.set()
            await message.answer("<b>❌ Цена не может быть меньше 0.</b>\n"
                                 "📁 Введите цену для позиции 💰")
    else:
        await StoragePosition.here_change_position_name.set()
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "📁 Введите цену для позиции 💰")


# Изменение описания позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_change_discription", state="*")
async def change_position_discription(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])
    async with state.proxy() as data:
        data["here_cache_category_id"] = category_id
        data["here_cache_position_id"] = position_id
        data["here_cache_position_remover"] = remover
    await StoragePosition.here_change_position_discription.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>📜 Введите новое описание для позиции</b>")


# Принятие описания позиции для её изменения
@dp.message_handler(IsAdmin(), state=StoragePosition.here_change_position_discription)
async def input_position_discription(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data["here_cache_category_id"]
        category_id = data["here_cache_position_id"]
        remover = data["here_cache_position_remover"]
    try:
        delete_msg = await message.answer(message.text)
        await bot.delete_message(message.chat.id, delete_msg.message_id)
        update_positionx(position_id, position_discription=message.text)

        messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
        await message.answer("<b>✅ Описание позиции было успешно изменено</b>", reply_markup=items_default)
        await state.finish()

        get_position = get_positionx("*", position_id=position_id)
        await bot.delete_message(message.from_user.id, message.message_id)
        if have_photo:
            await message.answer_photo(get_position[5], messages, reply_markup=keyboard)
        else:
            await message.answer(messages, reply_markup=keyboard)
    except CantParseEntities:
        await StoragePosition.here_change_position_discription.set()
        await bot.send_message(message.from_user.id,
                               "<b>❌ Ошибка синтаксиса HTML.</b>\n"
                               "📜 Введите новое описание для позиции")


# Изменение изображения позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_change_photo", state="*")
async def change_position_photo(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])
    async with state.proxy() as data:
        data["here_cache_category_id"] = category_id
        data["here_cache_position_id"] = position_id
        data["here_cache_position_remover"] = remover
    await StoragePosition.here_change_position_image.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>📸 Отправьте новое изображение для позиции</b>",
                           reply_markup=cancel_send_image_default)


# Отмена принятие изображения позиции для её изменения
@dp.message_handler(IsAdmin(), text="📸 Отменить", state=StoragePosition.here_change_position_image)
async def cancel_input_position_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data["here_cache_category_id"]
        category_id = data["here_cache_position_id"]
        remover = data["here_cache_position_remover"]
    update_positionx(position_id, position_image="")

    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
    await message.answer("<b>✅ Изображение позиции было успешно изменено</b>", reply_markup=items_default)
    await state.finish()

    get_position = get_positionx("*", position_id=position_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    if have_photo:
        await message.answer_photo(get_position[5], messages, reply_markup=keyboard)
    else:
        await message.answer(messages, reply_markup=keyboard)


# Принятие изображения позиции для её изменения
@dp.message_handler(content_types=["photo"], state=StoragePosition.here_change_position_image)
async def input_position_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data["here_cache_category_id"]
        category_id = data["here_cache_position_id"]
        remover = data["here_cache_position_remover"]
    update_positionx(position_id, position_image=message.photo[0].file_id)

    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
    await message.answer("<b>✅ Изображение позиции было успешно изменено</b>", reply_markup=items_default)
    await state.finish()

    get_position = get_positionx("*", position_id=position_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    if have_photo:
        await message.answer_photo(get_position[5], messages, reply_markup=keyboard)
    else:
        await message.answer(messages, reply_markup=keyboard)


# Удаление позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_remove_this", state="*")
async def open_category_for_create_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>📜 Вы действительно хотите удалить позицию?</b>",
                           reply_markup=confirm_remove_position_func(position_id, category_id, remover))


# Согласие удаления позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="yes_remove_position", state="*")
async def open_category_for_create_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    remove_itemx(position_id=position_id)
    remove_positionx(position_id=position_id)
    await bot.edit_message_text("<b>☑ Вы успешно удалили позицию и её товары</b>",
                                call.from_user.id,
                                call.message.message_id)

    get_positions = get_positionsx("*", category_id=category_id)
    if len(get_positions) >= 1:
        get_kb = position_open_edit_ap(remover, category_id)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id,
                               "<b>📁 Выберите нужную вам позицию 🖍</b>",
                               reply_markup=get_kb)


# Отмена удаления позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="not_remove_position", state="*")
async def open_category_for_create_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
    await state.finish()

    get_position = get_positionx("*", position_id=position_id)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    if have_photo:
        await bot.send_photo(call.from_user.id, get_position[5], messages, reply_markup=keyboard)
    else:
        await bot.send_message(call.from_user.id, messages, reply_markup=keyboard)


# Очистка позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="position_clear_this", state="*")
async def open_category_for_clear_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>📜 Вы действительно хотите очистить позицию?</b>",
                           reply_markup=confirm_clear_position_func(position_id, category_id, remover))


# Согласие очистики позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="yes_clear_position", state="*")
async def open_category_for_clear_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    remove_itemx(position_id=position_id)

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>☑ Вы успешно очистиили товары позиции</b>",
                           reply_markup=items_default)
    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
    await state.finish()

    get_position = get_positionx("*", position_id=position_id)
    if have_photo:
        await bot.send_photo(call.from_user.id, get_position[5], messages, reply_markup=keyboard)
    else:
        await bot.send_message(call.from_user.id, messages, reply_markup=keyboard)


# Отмена очистики позиции
@dp.callback_query_handler(IsAdmin(), text_startswith="not_clear_position", state="*")
async def open_category_for_clear_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    messages, keyboard, have_photo = open_edit_position_func(position_id, category_id, remover)
    await state.finish()

    get_position = get_positionx("*", position_id=position_id)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    if have_photo:
        await bot.send_photo(call.from_user.id, get_position[5], messages, reply_markup=keyboard)
    else:
        await bot.send_message(call.from_user.id, messages, reply_markup=keyboard)


################################################################################################
###################################### УДАЛЕНИЕ ВСЕХ ПОЗИЦИЙ ###################################
# Согласие на удаление всех позиций и товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_clear_position", state="*")
async def create_input_position_name(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    delete_msg = await bot.send_message(call.from_user.id, "<b>⌛ Ждите, позиции удаляются...</b>")
    get_positions = len(get_all_positionsx())
    get_items = len(get_all_itemsx())

    clear_positionx()
    clear_itemx()
    await bot.edit_message_text(f"<b>☑ Вы успешно удалили все позиции({get_positions}шт) и товары({get_items}шт)</b>",
                                call.from_user.id,
                                delete_msg.message_id)


# Отмена удаления категорий
@dp.callback_query_handler(IsAdmin(), text_startswith="cancel_clear_position", state="*")
async def create_input_position_name(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text("<b>☑ Вы отменили удаление всех позиций</b>",
                                call.from_user.id,
                                call.message.message_id)


################################################################################################
####################################### ДОБАВЛЕНИЕ ТОВАРОВ #####################################
# Возвращение к начальным категориям для добавления товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="back_add_item_to_category", state="*")
async def back_to_all_categories_for_add_item(call: CallbackQuery, state: FSMContext):
    get_kb = item_open_add_category_ap(0)

    await bot.edit_message_text("<b>🎁 Выберите категорию с нужной вам позицией ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Сделующая страница выбора категории с позицией для добавления товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="add_item_category_nextp", state="*")
async def next_page_category_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = item_add_next_page_category_ap(remover)
    await bot.edit_message_text("<b>🎁 Выберите категорию с нужной вам позицией ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Предыдущая страница выбора категории с позицией для добавления товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="add_item_category_prevp", state="*")
async def previous_page_category_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    get_kb = item_add_previous_page_category_ap(remover)
    await bot.edit_message_text("<b>🎁 Выберите категорию с нужной вам позицией ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Выбор категории с нужной позицией
@dp.callback_query_handler(IsAdmin(), text_startswith="item_add_category", state="*")
async def open_category_for_edit_position(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])

    get_positions = get_positionsx("*", category_id=category_id)
    if len(get_positions) >= 1:
        get_kb = position_add_item_position_ap(0, category_id)
        await bot.edit_message_text("<b>🎁 Выберите нужную вам позицию ➕</b>",
                                    call.from_user.id,
                                    call.message.message_id,
                                    reply_markup=get_kb)
    else:
        await bot.answer_callback_query(call.id, "🎁 Позиции в данной категории отсутствуют")


# Сделующая страница позиций для добавления товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="add_item_position_nextp", state="*")
async def next_page_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    get_kb = position_edit_next_page_position_ap(remover, category_id)
    await bot.edit_message_text("<b>🎁 Выберите нужную вам позицию ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Предыдущая страница позиций для добавления товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="add_item_position_prevp", state="*")
async def previous_page_for_edit_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    get_kb = position_edit_previous_page_position_ap(remover, category_id)
    await bot.edit_message_text("<b>🎁 Выберите нужную вам позицию ➕</b>",
                                call.from_user.id,
                                call.message.message_id,
                                reply_markup=get_kb)


# Выбор позиции для добавления товаров
@rate_limit(0)
@dp.callback_query_handler(IsAdmin(), text_startswith="item_add_position", state="*")
async def open_for_edit_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    category_id = int(call.data.split(":")[3])
    async with state.proxy() as data:
        data["here_cache_add_item_category_id"] = category_id
        data["here_cache_add_item_position_id"] = position_id
        data["here_cache_add_item_remover"] = remover
        data["here_count_add_items"] = 0
    await StorageItems.here_add_items.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id,
                           "<b>📤 Отправьте данные товаров.</b>\n"
                           "❕ Товары можно добавлять любым удобным способом.\n"
                           "❗ Товары разделяются одной пустой строчкой. Пример:\n"
                           "<code>Логин: 123456789\nПароль: 123456789\n\n"
                           "Логин и пароль: 123456789:123456789\n\n"
                           "Прочие данные...</code>",
                           reply_markup=finish_load_items_default)


# Завершение загрузки товаров
@dp.message_handler(IsAdmin(), text="📥 Закончить загрузку товаров", state="*")
async def finish_load_items(message: types.Message, state: FSMContext):
    get_all_items = 0
    try:
        async with state.proxy() as data:
            get_all_items = data["here_count_add_items"]
    except:
        pass
    await state.finish()
    delete_msg = await message.answer("<b>📥 Загрузка товаров была успешно завершена ✅\n"
                                      f"▶ Загружено товаров:</b> <code>{get_all_items}шт</code>",
                                      reply_markup=items_default)


# Принятие данных товара
@rate_limit(0)
@dp.message_handler(IsAdmin(), state=StorageItems.here_add_items)
async def input_item_data(message: types.Message, state: FSMContext):
    delete_msg = await message.answer("<b>⌛ Ждите, товары добавляются...</b>")
    count_add = 0
    get_all_items = message.text.split("\n\n")
    for check_item in get_all_items:
        if not check_item.isspace() and check_item != "":
            count_add += 1
    async with state.proxy() as data:
        category_id = data["here_cache_add_item_category_id"]
        position_id = data["here_cache_add_item_position_id"]
        data["here_count_add_items"] += count_add
    add_itemx(category_id, position_id, get_all_items, message.from_user.id,
              clear_firstname(message.from_user.first_name))
    await bot.delete_message(message.from_user.id, delete_msg.message_id)
    await message.answer(f"<b>📥 Товары в кол-ве</b> <u>{count_add}шт</u> <b>были успешно добавлены ✅</b>")


################################################################################################
####################################### ИЗМЕНЕНИЕ ТОВАРОВ ######################################
# Согласие на удаление всех товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="delete_this_item", state="*")
async def delete_item(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await StorageItems.here_del_items.set()
    await bot.send_message(call.from_user.id,
                           "<b>🎁 Отправьте айди товаров для удаления</b>\n"
                           "❕ Если хотите удалить несколько товаров, отправьте ID товаров через запятую или пробел. Пример:\n"
                           "<code>▶ 123456,123456,123456</code>\n"
                           "<code>▶ 123456 123456 123456</code>")


# Принятие айди товаров для их удаления
@dp.message_handler(IsAdmin(), state=StorageItems.here_del_items)
async def input_item_id_for_delete(message: types.Message, state: FSMContext):
    remove_ids = []  # Айди удалённых товаров
    cancel_ids = []  # Айди ненайденных товаров
    if "," in message.text:
        get_item_ids = message.text.split(",")
    elif " " in message.text:
        get_item_ids = message.text.split(" ")
    else:
        get_item_ids = [message.text]

    for item_id in get_item_ids:
        check_item = get_itemx("*", item_id=item_id)
        if check_item is not None:
            remove_itemx(item_id=item_id)
            remove_ids.append(item_id)
        else:
            cancel_ids.append(item_id)
    remove_ids = ", ".join(remove_ids)
    cancel_ids = ", ".join(cancel_ids)
    await state.finish()
    await message.answer(f"<b>✅ Успешно удалённые товары:</b>\n"
                         f"<code>▶ {remove_ids}</code>\n"
                         f"➖➖➖➖➖➖➖➖➖➖\n"
                         f"<b>❌ Ненайденные товары:</b>\n"
                         f"<code>▶ {cancel_ids}</code>",
                         reply_markup=items_default)


################################################################################################
##################################### УДАЛЕНИЕ ВСЕХ ТОВАРОВ ####################################
# Согласие на удаление всех товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_clear_item", state="*")
async def confirm_clear_all_items(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    delete_msg = await bot.send_message(call.from_user.id, "<b>⌛ Ждите, товары удаляются...</b>")
    get_items = get_all_itemsx()

    clear_itemx()
    await bot.edit_message_text("<b>☑ Вы успешно удалили все товары</b>",
                                call.from_user.id,
                                delete_msg.message_id)


# Отмена удаления всех товаров
@dp.callback_query_handler(IsAdmin(), text_startswith="cancel_clear_item", state="*")
async def cancel_remove_all_items(call: CallbackQuery, state: FSMContext):
    await bot.edit_message_text("<b>☑ Вы отменили удаление всех товаров</b>",
                                call.from_user.id,
                                call.message.message_id)
