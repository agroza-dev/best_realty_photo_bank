from telegram import Update
from telegram.ext import ContextTypes

from api.crud.users import get_user_by_tg_id, create_user
from bot.handlers.helper import reset_user_data
from bot.utils.response import send_response
from utils.templates import render_bot_template
from core.models import db_helper, User
from core.schemas.user import UserCreate
from utils.logger import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    user = await db_helper.execute_with_session(get_user_by_tg_id, user_id)
    if user is None:
        new_user_create = UserCreate(
            username=message.from_user.username,
            telegram_id=message.from_user.id,
            last_name=message.from_user.last_name,
            first_name=message.from_user.first_name,
            is_deleted=1,
            can_upload=0,
            can_receive=0,
        )
        new_user: User = await db_helper.execute_with_session_scope(create_user, new_user_create)
        if new_user is None:
            logger.error(f"Error on create user {user_id} => {message.from_user.username}")
            raise ValueError("Ошибка! Не удалось инициализировать. ")

    reset_user_data(context)

    await send_response(update, context, response=render_bot_template("start.j2"))
