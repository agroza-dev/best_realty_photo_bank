from functools import wraps
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from typing import Callable

from api.crud.users import get_user_by_tg_id
from bot.utils.response import send_response
from core.models.static import Restrictions
from utils.templates import render_common_template
from core.models import db_helper


class AccessRestrictionError(Exception):
    def __init__(self, message: str, action: str, user_id: int, original_error: Exception = None):
        self.message = message
        self.action = action
        self.user_id = user_id
        self.original_error = original_error
        super().__init__(self.message)


def restrict_access(action: str):
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = 'unknown'
            try:
                if update.effective_user is None:
                    await update.message.reply_text(render_common_template("error_user_not_found.j2"))
                    return

                user_id = update.effective_user.id
                user = await db_helper.execute_with_session(get_user_by_tg_id, user_id)

                if user is None:
                    await send_response(update, context, response=render_common_template("error_user_not_found.j2"))
                    return

                if user.is_deleted:
                    await send_response(update, context, response=render_common_template("error_user_is_deactivated.j2"))
                    return

                if action == Restrictions.upload and not user.can_upload:
                    await send_response(update, context, response=render_common_template("error_user_can_not_upload.j2"))
                    return
                if action == Restrictions.receive and not user.can_receive:
                    await send_response(update, context, response=render_common_template("error_user_can_not_receive.j2"))
                    return

                if action == Restrictions.is_admin and not user.is_admin:
                    await send_response(update, context, response=render_common_template("error_user_is_not_admin.j2"))
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