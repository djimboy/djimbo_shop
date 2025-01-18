# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database import Categoryx, Itemx, Positionx, Userx
from tgbot.keyboards.inline_admin import close_finl
from tgbot.keyboards.inline_admin_page import (category_edit_swipe_fp, position_add_swipe_fp,
                                               position_edit_category_swipe_fp, position_edit_swipe_fp,
                                               item_add_position_swipe_fp, item_add_category_swipe_fp,
                                               item_delete_swipe_fp)
from tgbot.keyboards.inline_admin_products import (category_edit_delete_finl, position_edit_clear_finl,
                                                   position_edit_delete_finl, position_edit_cancel_finl,
                                                   category_edit_cancel_finl, products_removes_finl,
                                                   products_removes_categories_finl, products_removes_positions_finl,
                                                   products_removes_items_finl, item_add_finish_finl)
from tgbot.services.api_discord import DiscordAPI
from tgbot.utils.const_functions import clear_list, is_number, to_number, del_message, ded, get_unix, clear_html
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text
from tgbot.utils.text_functions import category_open_admin, position_open_admin, item_open_admin

router = Router(name=__name__)


# Создание новой категории
@router.callback_query(F.data == "inline_create_category")
async def prod_category_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_category_name")
    await call.message.edit_text("<b>🗃 Введите название для категории</b>")


# Выбор категории для редактирования
@router.callback_query(F.data == "inline_change_category")
async def prod_category_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>🗃 Выберите категорию для изменения 🖍</b>",
            reply_markup=category_edit_swipe_fp(0),
        )
    else:
        await call.answer("❌ Отсутствуют категории для изменения категорий", True)


# Создание новой позиции
@router.callback_query(F.data == "inline_create_position")
async def prod_position_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>📁 Выберите категорию для позиции ➕</b>",
            reply_markup=position_add_swipe_fp(0),
        )
    else:
        await call.answer("❌ Отсутствуют категории для создания позиции", True)


# Выбор позиции для редактирования
@router.callback_query(F.data == "inline_change_position")
async def prod_position_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>📁 Выберите позицию для изменения 🖍</b>",
            reply_markup=position_edit_category_swipe_fp(0),
        )
    else:
        await call.answer("❌ Отсутствуют категории для изменения позиций", True)


# Страницы товаров для добавления
@router.callback_query(F.data == "inline_add_goods")
async def prod_item_add(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>🎁 Выберите позицию для товаров ➕</b>",
            reply_markup=item_add_category_swipe_fp(0),
        )
    else:
        await call.answer("❌ Отсутствуют позиции для добавления товара", True)


# Удаление категорий, позиций или товаров
@router.callback_query(F.data == "inline_delete_items")
async def prod_removes(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.message.edit_text(
        "<b>🎁 Выберите раздел который хотите удалить ❌</b>\n",
        reply_markup=products_removes_finl(),
    )


################################################################################
############################### СОЗДАНИЕ КАТЕГОРИИ #############################
# Принятие названия категории для её создания
@router.message(F.text, StateFilter('here_category_name'))
async def prod_category_add_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "🗃 Введите название для категории",
        )

    await state.clear()

    category_id = get_unix()
    Categoryx.add(category_id, clear_html(message.text))

    await category_open_admin(bot, message.from_user.id, category_id, 0)


################################################################################
############################### ИЗМЕНЕНИЕ КАТЕГОРИИ ############################
# Страница выбора категорий для редактирования
@router.callback_query(F.data.startswith("category_edit_swipe:"))
async def prod_category_edit_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>🗃 Выберите категорию для изменения 🖍</b>",
        reply_markup=category_edit_swipe_fp(remover),
    )


# Выбор текущей категории для редактирования
@router.callback_query(F.data.startswith("category_edit_open:"))
async def prod_category_edit_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await state.clear()

    await del_message(call.message)
    await category_open_admin(bot, call.from_user.id, category_id, remover)


############################ САМО ИЗМЕНЕНИЕ КАТЕГОРИИ ##########################
# Изменение названия категории
@router.callback_query(F.data.startswith("category_edit_name:"))
async def prod_category_edit_name(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_category_edit_name")

    await del_message(call.message)

    await call.message.answer(
        "<b>🗃 Введите новое название для категории</b>",
        reply_markup=category_edit_cancel_finl(category_id, remover),
    )


# Принятие нового названия для категории
@router.message(F.text, StateFilter('here_category_edit_name'))
async def prod_category_edit_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    category_id = (await state.get_data())['here_category_id']
    remover = (await state.get_data())['here_remover']

    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "🗃 Введите новое название для категории",
            reply_markup=category_edit_cancel_finl(category_id, remover),
        )

    await state.clear()

    Categoryx.update(category_id, category_name=clear_html(message.text))
    await category_open_admin(bot, message.from_user.id, category_id, remover)


# Окно с уточнением удалить категорию
@router.callback_query(F.data.startswith("category_edit_delete:"))
async def prod_category_edit_delete(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await call.message.edit_text(
        "<b>❗ Вы действительно хотите удалить категорию и все её данные?</b>",
        reply_markup=category_edit_delete_finl(category_id, remover),
    )


# Отмена удаления категории
@router.callback_query(F.data.startswith("category_edit_delete_confirm:"))
async def prod_category_edit_delete_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    Categoryx.delete(category_id=category_id)
    Positionx.delete(category_id=category_id)
    Itemx.delete(category_id=category_id)

    await call.answer("🗃 Категория и все её данные были успешно удалены ✅")

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await call.message.edit_text(
            "<b>🗃 Выберите категорию для изменения 🖍</b>",
            reply_markup=category_edit_swipe_fp(remover),
        )
    else:
        await del_message(call.message)


################################################################################
############################### ДОБАВЛЕНИЕ ПОЗИЦИИ #############################
# Cтраницы выбора категорий для расположения позиции
@router.callback_query(F.data.startswith("position_add_swipe:"))
async def prod_position_add_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>📁 Выберите категорию для позиции ➕</b>",
        reply_markup=position_add_swipe_fp(remover),
    )


# Выбор категории для создания позиции
@router.callback_query(F.data.startswith("position_add_open:"))
async def prod_position_add_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])

    await state.update_data(here_category_id=category_id)
    await state.set_state("here_position_name")

    await call.message.edit_text("<b>📁 Введите название для позиции</b>")


# Принятие названия для создания позиции
@router.message(F.text, StateFilter('here_position_name'))
async def prod_position_add_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "📁 Введите название для позиции",
        )

    await state.update_data(here_position_name=clear_html(message.text))
    await state.set_state("here_position_price")

    await message.answer("<b>📁 Введите цену для позиции</b>")


# Принятие цены позиции для её создания
@router.message(F.text, StateFilter('here_position_price'))
async def prod_position_add_price_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно</b>\n"
            "📁 Введите цену для позиции",
        )

    if to_number(message.text) > 10_000_000 or to_number(message.text) < 0:
        return await message.answer(
            "<b>❌ Цена не может быть меньше 0₽ или больше 10 000 000₽</b>\n"
            "📁 Введите цену для позиции",
        )

    await state.update_data(here_position_price=to_number(message.text))
    await state.set_state("here_position_desc")

    await message.answer(
        "<b>📁 Введите описание для позиции</b>\n"
        "❕ Вы можете использовать HTML разметку\n"
        "❕ Отправьте <code>0</code> чтобы пропустить.",
    )


# Принятие описания позиции для её создания
@router.message(F.text, StateFilter('here_position_desc'))
async def prod_position_add_desc_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if len(message.text) > 1200:
        await message.answer(
            "<b>❌ Описание не может превышать 1200 символов</b>\n"
            "📁 Введите новое описание для позиции\n"
            "❕ Вы можете использовать HTML разметку\n"
            "❕ Отправьте <code>0</code> чтобы пропустить.",
        )

    try:
        if message.text != "0":
            await (await message.answer(message.text)).delete()

            position_desc = message.text
        else:
            position_desc = "None"
    except:
        return await message.answer(
            ded(f"""
                <b>❌ Ошибка синтаксиса HTML</b>
                📁 Введите описание для позиции
                ❕ Вы можете использовать HTML разметку
                ❕ Отправьте <code>0</code> чтобы пропустить
            """),
        )

    await state.update_data(here_position_desc=position_desc)
    await state.set_state("here_position_photo")

    await message.answer(
        "<b>📁 Отправьте изображение для позиции</b>\n"
        "❕ Отправьте <code>0</code> чтобы пропустить.",
    )


# Принятие изображения для позиции при её создании
@router.message((F.text == "0") | F.photo, StateFilter('here_position_photo'))
async def prod_position_add_photo_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    category_id = state_data['here_category_id']
    position_name = clear_html(state_data['here_position_name'])
    position_price = to_number(state_data['here_position_price'])
    position_desc = state_data['here_position_desc']
    position_id = get_unix()
    position_photo = "None"
    await state.clear()

    if message.photo is not None:
        cache_message = await message.answer(
            "<b>♻️ Подождите, фотография загружается...</b>"
        )

        file_path = (await bot.get_file(message.photo[-1].file_id)).file_path
        photo_path = await bot.download_file(file_path)

        pay_image_status, pay_image_url = await (DiscordAPI(
            bot=bot,
            arSession=arSession,
            update=message,
        )).upload_photo(photo_path.read())

        if pay_image_status:
            position_photo = pay_image_url

        await del_message(cache_message)

    Positionx.add(
        category_id=category_id,
        position_id=position_id,
        position_name=position_name,
        position_price=position_price,
        position_desc=position_desc,
        position_photo=position_photo,
    )

    await position_open_admin(bot, message.from_user.id, position_id)


################################################################################
############################### ИЗМЕНЕНИЕ ПОЗИЦИИ ##############################
# Перемещение по страницам категорий для редактирования позиции
@router.callback_query(F.data.startswith("position_edit_category_swipe:"))
async def prod_position_edit_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>📁 Выберите позицию для изменения 🖍</b>",
        reply_markup=position_edit_category_swipe_fp(remover),
    )


# Выбор категории с нужной позицией
@router.callback_query(F.data.startswith("position_edit_category_open:"))
async def prod_position_edit_category_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])

    get_category = Categoryx.get(category_id=category_id)
    get_positions = Positionx.gets(category_id=category_id)

    if len(get_positions) >= 1:
        await call.message.edit_text(
            "<b>📁 Выберите позицию для изменения 🖍</b>",
            reply_markup=position_edit_swipe_fp(0, category_id),
        )
    else:
        await call.answer(f"📁 Позиции в категории {get_category.category_name} отсутствуют")


# Перемещение по страницам позиций для редактирования позиции
@router.callback_query(F.data.startswith("position_edit_swipe:"))
async def prod_position_edit_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Выберите позицию для изменения 🖍</b>",
        reply_markup=position_edit_swipe_fp(remover, category_id),
    )


# Выбор позиции для редактирования
@router.callback_query(F.data.startswith("position_edit_open:"))
async def prod_position_edit_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.clear()

    await del_message(call.message)
    await position_open_admin(bot, call.from_user.id, position_id)


############################ САМО ИЗМЕНЕНИЕ ПОЗИЦИИ ############################
# Изменение названия позиции
@router.callback_query(F.data.startswith("position_edit_name:"))
async def prod_position_edit_name(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_name")

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Введите новое название для позиции</b>",
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие названия позиции для её изменения
@router.message(F.text, StateFilter('here_position_edit_name'))
async def prod_position_edit_name_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    position_id = state_data['here_position_id']
    category_id = state_data['here_category_id']
    remover = state_data['here_remover']

    if len(message.text) > 50:
        return await message.answer(
            "<b>❌ Название не может превышать 50 символов</b>\n"
            "📁 Введите новое название для позиции",
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    await state.clear()

    Positionx.update(position_id, position_name=clear_html(message.text))
    await position_open_admin(bot, message.from_user.id, position_id)


# Изменение цены позиции
@router.callback_query(F.data.startswith("position_edit_price:"))
async def prod_position_edit_price(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_price")

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Введите новую цену для позиции</b>",
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие цены позиции для её изменения
@router.message(F.text, StateFilter('here_position_edit_price'))
async def prod_position_edit_price_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    position_id = state_data['here_position_id']
    category_id = state_data['here_category_id']
    remover = state_data['here_remover']

    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно</b>\n"
            "📁 Введите новую цену для позиции",
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    if to_number(message.text) > 10_000_000 or to_number(message.text) < 0:
        return await message.answer(
            "<b>❌ Цена не может быть меньше 0₽ или больше 10 000 000₽</b>\n"
            "📁 Введите новую цену для позиции",
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    await state.clear()

    Positionx.update(position_id, position_price=to_number(message.text))
    await position_open_admin(bot, message.from_user.id, position_id)


# Изменение описания позиции
@router.callback_query(F.data.startswith("position_edit_desc:"))
async def prod_position_edit_desc(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_desc")

    await del_message(call.message)

    await call.message.answer(
        ded(f"""
            <b>📁 Введите новое описание для позиции</b>
            ❕ Вы можете использовать HTML разметку
            ❕ Отправьте <code>0</code> чтобы пропустить
        """),
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие описания позиции для её изменения
@router.message(F.text, StateFilter('here_position_edit_desc'))
async def prod_position_edit_desc_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()

    category_id = state_data['here_category_id']
    position_id = state_data['here_position_id']
    remover = state_data['here_remover']

    if len(message.text) > 1200:
        return await message.answer(
            ded(f"""
                <b>❌ Описание не может превышать 1200 символов</b>
                📁 Введите новое описание для позиции
                ❕ Вы можете использовать HTML разметку
                ❕ Отправьте <code>0</code> чтобы пропустить
            """),
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    try:
        if message.text != "0":
            await (await message.answer(message.text)).delete()

            position_desc = message.text
        else:
            position_desc = "None"
    except:
        return await message.answer(
            ded(f"""
                <b>❌ Ошибка синтаксиса HTML</b>
                📁 Введите новое описание для позиции
                ❕ Вы можете использовать HTML разметку
                ❕ Отправьте <code>0</code> чтобы пропустить
            """),
            reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
        )

    await state.clear()

    Positionx.update(position_id, position_desc=position_desc)
    await position_open_admin(bot, message.from_user.id, position_id)


# Изменение изображения позиции
@router.callback_query(F.data.startswith("position_edit_photo:"))
async def prod_position_edit_photo(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await state.update_data(here_position_id=position_id)
    await state.update_data(here_category_id=category_id)
    await state.update_data(here_remover=remover)
    await state.set_state("here_position_edit_photo")

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Отправьте новое изображение для позиции</b>\n"
        "❕ Отправьте <code>0</code> чтобы пропустить.",
        reply_markup=position_edit_cancel_finl(position_id, category_id, remover),
    )


# Принятие нового фото для позиции
@router.message((F.text == "0") | F.photo, StateFilter('here_position_edit_photo'))
async def prod_position_edit_photo_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    state_data = await state.get_data()
    await state.clear()

    position_id = state_data['here_position_id']
    category_id = state_data['here_category_id']
    remover = state_data['here_remover']
    position_photo = "None"

    if message.photo is not None:
        cache_message = await message.answer(
            "<b>♻️ Подождите, фотография загружается...</b>"
        )

        file_path = (await bot.get_file(message.photo[-1].file_id)).file_path
        photo_path = await bot.download_file(file_path)

        pay_image_status, pay_image_url = await (DiscordAPI(
            bot=bot,
            arSession=arSession,
            update=message,
        )).upload_photo(photo_path.read())

        if pay_image_status:
            position_photo = pay_image_url

        await del_message(cache_message)

    Positionx.update(position_id, position_photo=position_photo)
    await position_open_admin(bot, message.from_user.id, position_id)


# Выгрузка товаров
@router.callback_query(F.data.startswith("position_edit_items:"))
async def prod_position_edit_items(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    get_position = Positionx.get(position_id=position_id)
    get_items = Itemx.gets(position_id=position_id)

    if len(get_items) >= 1:
        save_items = "\n\n".join([item.item_data for item in get_items])
        save_items = await upload_text(arSession, save_items)

        await call.message.answer(
            f"<b>🎁 Все товары позиции: <code>{get_position.position_name}</code>\n"
            f"🔗 Ссылка: <a href='{save_items}'>кликабельно</a></b>",
            reply_markup=close_finl(),
        )
        await call.answer(cache_time=5)
    else:
        await call.answer("❕ В данной позиции отсутствуют товары", True)


# Удаление позиции
@router.callback_query(F.data.startswith("position_edit_delete:"))
async def prod_position_edit_delete(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Вы действительно хотите удалить позицию? ❌</b>",
        reply_markup=position_edit_delete_finl(position_id, category_id, remover),
    )


# Подтверждение удаления позиции
@router.callback_query(F.data.startswith("position_edit_delete_confirm:"))
async def prod_position_edit_delete_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    Itemx.delete(position_id=position_id)
    Positionx.delete(position_id=position_id)

    await call.answer("📁 Вы успешно удалили позицию и её товары ✅")

    if len(Positionx.gets(category_id=category_id)) >= 1:
        await call.message.edit_text(
            "<b>📁 Выберите позицию для изменения 🖍</b>",
            reply_markup=position_edit_swipe_fp(remover, category_id),
        )
    else:
        await del_message(call.message)


# Очистка позиции
@router.callback_query(F.data.startswith("position_edit_clear:"))
async def prod_position_edit_clear(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    await del_message(call.message)

    await call.message.answer(
        "<b>📁 Вы хотите удалить все товары в позиции?</b>",
        reply_markup=position_edit_clear_finl(position_id, category_id, remover),
    )


# Согласие очистики позиции
@router.callback_query(F.data.startswith("position_edit_clear_confirm:"))
async def prod_position_edit_clear_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    Itemx.delete(position_id=position_id)
    await call.answer("📁 Вы успешно удалили все товары в позиции ✅")

    await del_message(call.message)
    await position_open_admin(bot, call.from_user.id, position_id)


################################################################################
############################### ДОБАВЛЕНИЕ ТОВАРОВ #############################
# Перемещение по страницам категорий для добавления товаров
@router.callback_query(F.data.startswith("item_add_category_swipe:"))
async def prod_item_add_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>🎁 Выберите позицию для товаров ➕</b>",
        reply_markup=item_add_category_swipe_fp(remover),
    )


# Выбор категории с нужной позицией
@router.callback_query(F.data.startswith("item_add_category_open:"))
async def prod_item_add_category_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_category = Categoryx.get(category_id=category_id)
    get_positions = Positionx.gets(category_id=category_id)

    await del_message(call.message)

    if len(get_positions) >= 1:
        await call.message.answer(
            "<b>🎁 Выберите позицию для товаров ➕</b>",
            reply_markup=item_add_position_swipe_fp(0, category_id),
        )
    else:
        await call.answer(f"🎁 Позиции в категории {get_category.category_name} отсутствуют")


# Перемещение по страницам позиций для добавления товаров
@router.callback_query(F.data.startswith("item_add_position_swipe:"))
async def prod_item_add_position_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await call.message.edit_text(
        "<b>🎁 Выберите позицию для товаров ➕</b>",
        reply_markup=item_add_position_swipe_fp(remover, category_id),
    )


# Выбор позиции для добавления товаров
@router.callback_query(F.data.startswith("item_add_position_open:"), flags={'rate': 0})
async def prod_item_add_position_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])

    await state.update_data(here_add_item_category_id=category_id)
    await state.update_data(here_add_item_position_id=position_id)
    await state.update_data(here_add_item_count=0)
    await state.set_state("here_add_items")

    await del_message(call.message)

    await call.message.answer(
        ded(f"""
            <b>🎁 Отправляйте данные товаров</b>
            ❗ Товары разделяются одной пустой строчкой. Пример:
            <code>Данные товара...

            Данные товара...

            Данные товара...</code>
        """),
        reply_markup=item_add_finish_finl(position_id),
    )


# Завершение загрузки товаров
@router.callback_query(F.data.startswith('item_add_position_finish:'), flags={'rate': 0})
async def prod_item_add_finish(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[1])

    try:
        count_items = (await state.get_data())['here_add_item_count']
    except:
        count_items = 0

    await state.clear()

    await call.message.edit_reply_markup()
    await call.message.answer(
        "<b>🎁 Загрузка товаров была успешно завершена ✅\n"
        f"❕ Загружено товаров: <code>{count_items}шт</code></b>",
    )

    await position_open_admin(bot, call.from_user.id, position_id)


# Принятие данных товара
@router.message(F.text, StateFilter('here_add_items'), flags={'rate': 0})
async def prod_item_add_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    cache_message = await message.answer("<b>⌛ Ждите, товары добавляются..</b>")

    get_items = clear_list(message.text.split("\n\n"))

    item_count = (await state.get_data())['here_add_item_count']
    category_id = (await state.get_data())['here_add_item_category_id']
    position_id = (await state.get_data())['here_add_item_position_id']

    await state.update_data(here_add_item_count=item_count + len(get_items))

    get_user = Userx.get(user_id=message.from_user.id)
    Itemx.add(
        user_id=get_user.user_id,
        category_id=category_id,
        position_id=position_id,
        item_datas=get_items,
    )

    await cache_message.edit_text(
        f"<b>🎁 Товары в кол-ве <u>{len(get_items)}шт</u> были успешно добавлены ✅</b>",
        reply_markup=item_add_finish_finl(position_id),
    )


################################################################################
############################### УДАЛЕНИЕ ТОВАРОВ ###############################
# Страницы удаления товаров
@router.callback_query(F.data.startswith("item_delete_swipe:"))
async def prod_item_delete_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])

    get_items = Itemx.gets(position_id=position_id)
    get_position = Positionx.get(position_id=position_id)

    if len(get_items) >= 1:
        await del_message(call.message)

        await call.message.answer(
            "<b>🎁 Выберите товар для удаления</b>",
            reply_markup=item_delete_swipe_fp(remover, position_id, category_id),
        )
    else:
        await call.answer(f"🎁 Товары в позиции {get_position.position_name} отсутствуют", True)


# Удаление товара
@router.callback_query(F.data.startswith("item_delete_open:"))
async def prod_item_delete_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    item_id = call.data.split(":")[1]

    await del_message(call.message)
    await item_open_admin(bot, call.from_user.id, item_id, 0)


# Подтверждение удаления товара
@router.callback_query(F.data.startswith("item_delete_confirm:"))
async def prod_item_delete_confirm_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    item_id = call.data.split(":")[1]

    get_item = Itemx.get(item_id=item_id)
    get_items = Itemx.gets(position_id=get_item.position_id)

    Itemx.delete(item_id=item_id)

    await call.message.edit_text(
        ded(f"""
            <b>✅ Товар был успешно удалён</b>
            ➖➖➖➖➖➖➖➖➖➖
            🎁️ Товар: <code>{get_item.item_data}</code>
        """)
    )

    if len(get_items) >= 1:
        await call.message.answer(
            "<b>🎁 Выберите товар для удаления</b>",
            reply_markup=item_delete_swipe_fp(0, get_item.position_id, get_item.category_id),
        )


################################################################################
############################### УДАЛЕНИЕ РАЗДЕЛОВ ##############################
# Возвращение к меню удаления разделов
@router.callback_query(F.data == "prod_removes_return")
async def prod_removes_return(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.message.edit_text(
        "<b>🎁 Выберите раздел который хотите удалить ❌</b>\n",
        reply_markup=products_removes_finl(),
    )


# Удаление всех категорий
@router.callback_query(F.data == "prod_removes_categories")
async def prod_removes_categories(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_categories = len(Categoryx.get_all())
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    await call.message.edit_text(
        ded(f"""
            <b>❌ Вы действительно хотите удалить все категории, позиции и товары?</b>
            🗃 Категорий: <code>{get_categories}шт</code>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """),
        reply_markup=products_removes_categories_finl(),
    )


# Подтверждение удаления всех категорий (позиций и товаров включительно)
@router.callback_query(F.data == "prod_removes_categories_confirm")
async def prod_removes_categories_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_categories = len(Categoryx.get_all())
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    Categoryx.clear()
    Positionx.clear()
    Itemx.clear()

    await call.message.edit_text(
        ded(f"""
            <b>✅ Вы успешно удалили все категории</b>
            🗃 Категорий: <code>{get_categories}шт</code>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """)
    )


# Удаление всех позиций
@router.callback_query(F.data == "prod_removes_positions")
async def prod_removes_positions(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    await call.message.edit_text(
        ded(f"""
            <b>❌ Вы действительно хотите удалить все позиции и товары?</b>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """),
        reply_markup=products_removes_positions_finl(),
    )


# Подтверждение удаления всех позиций (товаров включительно)
@router.callback_query(F.data == "prod_removes_positions_confirm")
async def prod_position_remove(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_positions = len(Positionx.get_all())
    get_items = len(Itemx.get_all())

    Positionx.clear()
    Itemx.clear()

    await call.message.edit_text(
        ded(f"""
            <b>✅ Вы успешно удалили все позиции</b>
            📁 Позиций: <code>{get_positions}шт</code>
            🎁 Товаров: <code>{get_items}шт</code>
        """)
    )


# Удаление всех товаров
@router.callback_query(F.data == "prod_removes_items")
async def prod_removes_items(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_items = len(Itemx.get_all())

    await call.message.edit_text(
        f"<b>❌ Вы действительно хотите удалить все товары?</b>\n"
        f"🎁 Товаров: <code>{get_items}шт</code>",
        reply_markup=products_removes_items_finl(),
    )


# Согласие на удаление всех товаров
@router.callback_query(F.data == "prod_removes_items_confirm")
async def prod_item_remove(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_items = len(Itemx.get_all())

    Itemx.clear()

    await call.message.edit_text(
        f"<b>✅ Вы успешно удалили все товары</b>\n"
        f"🎁 Товаров: <code>{get_items}шт</code>"
    )
