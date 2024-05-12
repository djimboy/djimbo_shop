# - *- coding: utf- 8 - *-
import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_position import Positionx
from tgbot.database.db_purchases import Purchasesx
from tgbot.database.db_users import Userx
from tgbot.keyboards.inline_user_prod import products_confirm_finl, products_return_finl
from tgbot.keyboards.inline_user_page import *
from tgbot.keyboards.reply_main import menu_frep
from tgbot.utils.const_functions import split_messages, get_unix, ded, del_message, convert_date, gen_id
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import get_positions_items
from tgbot.utils.text_functions import position_open_user

router = Router(name=__name__)


# Страницы выбора категории для покупки товара
@router.callback_query(F.data.startswith("buy_category_swipe:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text(
        "<b>🎁 Выберите нужный вам товар</b>",
        reply_markup=prod_item_category_swipe_fp(remover),
    )


# Открытие категории с выбором позиции для покупки товара
@router.callback_query(F.data.startswith("buy_category_open:"))
async def user_buy_category_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_category = Categoryx.get(category_id=category_id)
    get_positions = get_positions_items(category_id)

    if len(get_positions) >= 1:
        await del_message(call.message)

        await call.message.answer(
            f"<b>🎁 Текущая категория: <code>{get_category.category_name}</code></b>",
            reply_markup=prod_item_position_swipe_fp(remover, category_id),
        )
    else:
        if remover == 0:
            await call.message.edit_text("<b>🎁 Увы, товары в данное время отсутствуют.</b>")
            await call.answer("❗ Позиции были изменены или удалены")
        else:
            await call.answer(
                f"❕ Товары в категории {get_category.category_name} отсутствуют",
                True,
                cache_time=5,
            )


# Страницы выбора позиции для покупки товара
@router.callback_query(F.data.startswith("buy_position_swipe:"))
async def user_buy_position_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    category_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_category = Categoryx.get(category_id=category_id)

    await del_message(call.message)
    await call.message.answer(
        f"<b>🎁 Текущая категория: <code>{get_category.category_name}</code></b>",
        reply_markup=prod_item_position_swipe_fp(remover, category_id),
    )


# Открытие позиции для покупки
@router.callback_query(F.data.startswith("buy_position_open:"))
async def user_buy_position_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    await state.clear()

    await del_message(call.message)
    await position_open_user(bot, call.from_user.id, position_id, remover)


#################################### ПОКУПКА ###################################
# Выбор количества товаров для покупки
@router.callback_query(F.data.startswith("buy_item_open:"))
async def user_buy_open(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])

    get_position = Positionx.get(position_id=position_id)
    get_items = Itemx.gets(position_id=position_id)
    get_user = Userx.get(user_id=call.from_user.id)

    # Проверка, имеется ли на балансе пользователя достаточно средств
    if int(get_user.user_balance) < int(get_position.position_price):
        return await call.answer("❗ У вас недостаточно средств. Пополните баланс", True)

    if len(get_items) < 1:
        return await call.answer("❗ Товаров нет в наличии", True)

    # Максимальное количество товаров к покупке, подстроенные под баланс пользователя
    if get_position.position_price != 0:
        get_count = round(int(get_user.user_balance / get_position.position_price), 2)

        if get_count > len(get_items):
            get_items = len(get_items)
        else:
            get_items = get_count
    else:
        get_items = len(get_items)

    # Если в наличии всего один товар, то пропустить ввод количества товаров к покупке
    if get_items == 1:
        await state.clear()

        await del_message(call.message)

        await call.message.answer(
            ded(f"""
                <b>🎁 Вы действительно хотите купить товар(ы)?</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Товар: <code>{get_position.position_name}</code>
                ▪️ Количество: <code>1шт</code>
                ▪️ Сумма к покупке: <code>{get_position.position_price}₽</code>
            """),
            reply_markup=products_confirm_finl(position_id, get_position.category_id, 1),
        )
    else:
        await state.update_data(here_buy_position_id=position_id)
        await state.set_state("here_item_count")

        await del_message(call.message)

        await call.message.answer(
            ded(f"""
                <b>🎁 Введите количество товаров для покупки</b>
                ❕ От <code>1</code> до <code>{get_items}</code>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Товар: <code>{get_position.position_name}</code> - <code>{get_position.position_price}₽</code>
                ▪️ Ваш баланс: <code>{get_user.user_balance}₽</code>
            """),
            reply_markup=products_return_finl(position_id, get_position.category_id),
        )


# Принятие количества товаров для покупки
@router.message(F.text, StateFilter("here_item_count"))
async def user_buy_count(message: Message, bot: Bot, state: FSM, arSession: ARS):
    position_id = (await state.get_data())['here_buy_position_id']

    get_position = Positionx.get(position_id=position_id)
    get_user = Userx.get(user_id=message.from_user.id)
    get_items = Itemx.gets(position_id=position_id)

    # Максимальное количество товаров к покупке, подстроенные под баланс пользователя
    if get_position.position_price != 0:
        get_count = int(get_user.user_balance / get_position.position_price)

        if get_count > len(get_items):
            get_count = len(get_items)
    else:
        get_count = len(get_items)

    send_message = ded(f"""
        🎁 Введите количество товаров для покупки
        ❕ От <code>1</code> до <code>{get_count}</code>
        ➖➖➖➖➖➖➖➖➖➖
        ▪️ Товар: <code>{get_position.position_name}</code> - <code>{get_position.position_price}₽</code>
        ▪️ Ваш баланс: <code>{get_user.user_balance}₽</code>
    """)

    # Если было введено не число
    if not message.text.isdigit():
        return await message.answer(
            f"<b>❌ Данные были введены неверно.</b>\n" + send_message,
            reply_markup=products_return_finl(position_id, get_position.category_id),
        )

    get_count = int(message.text)
    amount_pay = round(get_position.position_price * get_count, 2)

    # Если товаров нет в наличии
    if len(get_items) < 1:
        await state.clear()
        return await message.answer("<b>🎁 Товар который вы хотели купить, закончился</b>")

    # Если товаров меньше 1 или меньше наличия
    if get_count < 1 or get_count > len(get_items):
        return await message.answer(
            f"<b>❌ Неверное количество товаров.</b>\n" + send_message,
            reply_markup=products_return_finl(position_id, get_position.category_id),
        )

    # Если баланс пользователя меньше, чем цена покупки
    if int(get_user.user_balance) < amount_pay:
        return await message.answer(
            f"<b>❌ Недостаточно средств на счете.</b>\n" + send_message,
            reply_markup=products_return_finl(position_id, get_position.category_id),
        )

    await state.clear()

    await message.answer(
        ded(f"""
            <b>🎁 Вы действительно хотите купить товар(ы)?</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Товар: <code>{get_position.position_name}</code>
            ▪️ Количество: <code>{get_count}шт</code>
            ▪️ Сумма к покупке: <code>{amount_pay}₽</code>
        """),
        reply_markup=products_confirm_finl(position_id, get_position.category_id, get_count),
    )


# Подтверждение покупки товара
@router.callback_query(F.data.startswith("buy_item_confirm:"))
async def user_buy_confirm(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    position_id = int(call.data.split(":")[1])
    purchase_count = int(call.data.split(":")[2])

    get_items = Itemx.gets(position_id=position_id)

    # Проверка наличия нужного количества товаров
    if purchase_count > len(get_items):
        return await call.message.edit_text(
            "<b>🎁 Товар который вы хотели купить закончился или изменился.</b>",
        )

    await call.message.edit_text("<b>🔄 Ждите, товары подготавливаются</b>")

    get_position = Positionx.get(position_id=position_id)
    get_category = Categoryx.get(category_id=get_position.category_id)
    get_user = Userx.get(user_id=call.from_user.id)

    purchase_price = round(get_position.position_price * purchase_count, 2)

    # Проверка баланса пользователя и общей суммы покупки
    if get_user.user_balance < purchase_price:
        return await call.message.answer("<b>❗ На вашем счёте недостаточно средств</b>")

    save_items, save_len = Itemx.buy(get_items, purchase_count)
    save_count = len(save_items)

    # Если в наличии оказалось меньше товаров, чем было запрошено
    if purchase_count != save_count:
        purchase_price = round(get_position.position_price * save_count, 2)
        purchase_count = save_count

    Userx.update(
        get_user.user_id,
        user_balance=round(get_user.user_balance - purchase_price, 2),
    )

    purchase_receipt = gen_id()
    purchase_unix = get_unix()
    purchase_data = "\n".join(save_items)

    Purchasesx.add(
        get_user.user_id,
        get_user.user_balance,
        round(get_user.user_balance - purchase_price, 2),
        purchase_receipt,
        purchase_data,
        purchase_count,
        purchase_price,
        get_position.position_price,
        get_position.position_id,
        get_position.position_name,
        get_category.category_id,
        get_category.category_name,
    )

    await del_message(call.message)

    for item in split_messages(save_items, save_len):
        await call.message.answer("\n\n".join(item), parse_mode="None")
        await asyncio.sleep(0.3)

    await call.message.answer(
        ded(f"""
            <b>✅ Вы успешно купили товар(ы)</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Чек: <code>#{purchase_receipt}</code>
            ▪️ Товар: <code>{get_position.position_name} | {purchase_count}шт | {purchase_price}₽</code>
            ▪️ Дата покупки: <code>{convert_date(purchase_unix)}</code>
        """),
        reply_markup=menu_frep(call.from_user.id),
    )
