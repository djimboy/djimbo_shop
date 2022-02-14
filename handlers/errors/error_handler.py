import logging

from aiogram.types import Update
from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError, UserDeactivated,
                                      CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
                                      MessageTextIsEmpty, RetryAfter, CantParseEntities, MessageCantBeDeleted,
                                      TerminatedByOtherGetUpdates, BotBlocked)

from loader import dp


@dp.errors_handler()
async def errors_handler(update, exception):
    if isinstance(exception, CantDemoteChatCreator):
        logging.exception(f"CantDemoteChatCreator: {exception}\nUpdate: {update}")
        return True

    # Не удалось изменить сообщение
    if isinstance(exception, MessageNotModified):
        logging.exception(f"MessageNotModified: {exception}\nUpdate: {update}")
        return True

    # Блокировка бота пользователем
    if isinstance(exception, BotBlocked):
        # logging.exception(f"BotBlocked: {exception}\nUpdate: {update}")
        return True

    # Не удалось удалить сообщение
    if isinstance(exception, MessageCantBeDeleted):
        logging.exception(f"MessageCantBeDeleted: {exception}\nUpdate: {update}")
        return True

    # Сообщение для удаления не было найдено
    if isinstance(exception, MessageToDeleteNotFound):
        # logging.exception(f"MessageToDeleteNotFound: {exception}\nUpdate: {update}")
        return True

    # Сообщение пустое
    if isinstance(exception, MessageTextIsEmpty):
        logging.exception(f"MessageTextIsEmpty: {exception}\nUpdate: {update}")
        return True

    # Пользователь удалён
    if isinstance(exception, UserDeactivated):
        return True

    # Бот не авторизован
    if isinstance(exception, Unauthorized):
        logging.exception(f"Unauthorized: {exception}\nUpdate: {update}")
        return True

    # Неверный Query ID
    if isinstance(exception, InvalidQueryID):
        logging.exception(f"InvalidQueryID: {exception}\nUpdate: {update}")
        return True

    # Повторите попытку позже
    if isinstance(exception, RetryAfter):
        logging.exception(f"RetryAfter: {exception}\nUpdate: {update}")
        return True

    # Уже имеется запущенный бот
    if isinstance(exception, TerminatedByOtherGetUpdates):
        print("You already have an active bot. Turn it off.")
        logging.exception(f"TerminatedByOtherGetUpdates: {exception}\nUpdate: {update}")
        return True

    # Ошибка в HTML/MARKDOWN разметке
    if isinstance(exception, CantParseEntities):
        logging.exception(f"CantParseEntities: {exception}\nUpdate: {update}")
        await Update.get_current().message.answer(f"❗ Ошибка HTML разметки\n"
                                                  f"`▶ {exception.args}`\n"
                                                  f"❕ Выполните заново действие с правильной разметкой тэгов.",
                                                  parse_mode="Markdown")
        return True

    # Ошибка телеграм АПИ
    if isinstance(exception, TelegramAPIError):
        logging.exception(f"TelegramAPIError: {exception}\nUpdate: {update}")
        return True

    # Все прочие ошибки
    logging.exception(f"Update: {update} \n{exception}")
