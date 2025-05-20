from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.restrict_access import AccessRestrictionError
from utils.logger import logger


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error
    user_id = update.effective_user.id if update and update.effective_user else "unknown"

    if isinstance(error, AccessRestrictionError):
        logger.error(
            f"AccessRestrictionError: action={error.action}, user_id={error.user_id}, "
            f"message={error.message}, original_error={error.original_error}"
        )
        if update and update.message:
            await update.message.reply_text(
                f"Произошла ошибка: {error.message}. Пожалуйста, обратитесь к администратору."
            )
    else:
        logger.error(f"Unexpected error for user {user_id}: {error}", exc_info=True)
        if update and update.message:
            await update.message.reply_text(
                "Произошла неизвестная ошибка. Пожалуйста, попробуйте позже."
            )
