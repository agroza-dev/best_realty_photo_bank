from functools import wraps
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from typing import Callable

from api.crud.users import get_user_by_tg_id
from bot.utils.templates import render_template
from core.models import db_helper


class AccessRestrictionError(Exception):
    def __init__(self, message: str, action: str, user_id: int, original_error: Exception = None):
        self.message = message
        self.action = action
        self.user_id = user_id
        self.original_error = original_error
        super().__init__(self.message)


class Restrictions:
    full = 'is_deleted'
    upload = 'upload'
    receive = 'receive'


def restrict_access(action: str):
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = 'unknown'
            try:
                if update.effective_user is None:
                    await update.message.reply_text(render_template("error_user_not_found.j2"))
                    return

                user_id = update.effective_user.id
                user = await db_helper.execute_with_session(get_user_by_tg_id, user_id)
                print(user)

                if user is None:
                    await update.message.reply_text(render_template("error_user_not_found.j2"))
                    return

                if user.is_deleted:
                    await update.message.reply_text(render_template("error_user_is_deactivated.j2"))
                    return

                if action == "upload" and not user.can_upload:
                    await update.message.reply_text(render_template("error_user_can_not_upload.j2"))
                    return
                if action == "receive" and not user.can_receive:
                    await update.message.reply_text(render_template("error_user_can_not_receive.j2"))
                    return

                return await handler(update, context)

            except AccessRestrictionError as e:
                raise e

            except TelegramError as e:
                raise AccessRestrictionError(
                    message=f"Telegram API error during access check",
                    action=action,
                    user_id=user_id,
                    original_error=e
                )

            except Exception as e:
                raise AccessRestrictionError(
                    message=f"Unexpected error during access check",
                    action=action,
                    user_id=user_id,
                    original_error=e
                )
        return wrapper
    return decorator