from telegram import Update
from telegram.ext import ContextTypes

from api.crud.users import get_user_by_tg_id, create_user
from bot.utils.response import send_response
from bot.utils.templates import render_template
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
        )
        new_user: User = await db_helper.execute_with_session_scope(create_user, new_user_create)
        if new_user is None:
            # TODO: do some error
            logger.error(f"Error on create user {user_id} => {message.from_user.username}")

    await send_response(update, context, response=render_template("start.j2"))
