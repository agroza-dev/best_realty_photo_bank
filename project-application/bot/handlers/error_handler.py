from telegram.ext import ContextTypes

from utils.logger import logger


async def handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Произошла ошибка: {context.error} данные пользователя: {context.user_data}")
