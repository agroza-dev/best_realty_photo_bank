from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import ContextTypes

from api.crud.users import get_user_by_tg_id, update_user
from bot.handlers.commands import set_user_specific_commands
from core import models
from core.config import settings
from core.models import db_helper
from core.schemas.user import UserUpdate



async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args
    if not args[0]:
        return
    target_user_id = int(args[0])

    if settings.app.super_admin == user_id:
        target_user = await db_helper.execute_with_session(get_user_by_tg_id, target_user_id)
        if target_user is not None and not target_user.is_admin:
            user_update = UserUpdate(is_admin=True, is_deleted=False, can_upload=True, can_receive=True)
            updated_user = await models.db_helper.execute_with_session_scope(update_user, target_user.id, user_update)
            await set_user_specific_commands(context.application, updated_user.telegram_id)
            await context.bot.setMessageReaction(
                update.message.chat_id,
                update.message.message_id,
                reaction=ReactionEmoji.THUMBS_UP
            )
        else:
            await context.bot.setMessageReaction(
                update.message.chat_id,
                update.message.message_id,
                reaction=ReactionEmoji.BROKEN_HEART
            )
    else:
        await context.bot.setMessageReaction(
            update.message.chat_id,
            update.message.message_id,
            reaction=ReactionEmoji.THUMBS_DOWN
        )