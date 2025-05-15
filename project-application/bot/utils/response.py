from typing import cast

import telegram
from telegram import Chat, InlineKeyboardMarkup, Update, InputMediaPhoto, Message
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bot.handlers.helper import do_with_retry
from utils.logger import logger


async def send_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> Message:
    args = {
        "chat_id": _get_chat_id(update),
        "disable_web_page_preview": True,
        "text": response,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    return await do_with_retry(context.bot.send_message, **args, label='send_response')


async def delete_message(message_id, update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await do_with_retry(update.effective_chat.delete_message, message_id, label='delete_message')

    except BadRequest as e:
        if "Message can't be deleted for everyone" in str(e):
            logger.warning(f"[delete_message] Сообщение {message_id} не может быть удалено: {e} очищаем куку.")
            context.user_data['last_message_id'] = False

        else:
            logger.error(f"[delete_message] BadRequest: {e}")
            raise

    except Exception as e:
        logger.exception(f"[delete_message] Необработанное исключение: {e}")
        raise


async def send_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    photo: str,
    keyboard: InlineKeyboardMarkup | None = None,
    update_message: bool = False
) -> None:
    args = {
        "chat_id": _get_chat_id(update),
        "caption": text,
        "photo": photo,
        "parse_mode": telegram.constants.ParseMode.HTML,
    }
    if keyboard:
        args["reply_markup"] = keyboard
    if update_message and hasattr(update, 'callback_query') and update.callback_query:
        if not keyboard:
            await update.callback_query.edit_message_media(
                media=InputMediaPhoto(
                    media=open(args['photo'], 'rb'),
                    caption=args['caption'],
                    parse_mode=args['parse_mode']
                )
            )
        else:
            await update.callback_query.edit_message_media(
                media=InputMediaPhoto(
                    media=open(args['photo'], 'rb'),
                    caption=args['caption'],
                    parse_mode=args['parse_mode']
                ),
                reply_markup=keyboard
            )
    else:
        await context.bot.send_photo(**args)


def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
