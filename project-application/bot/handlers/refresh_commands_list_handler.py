from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import ContextTypes

from api.crud.categories import CategoryFilter, get_category, create_category
from api.crud.filter import FieldFilter
from bot.decorators.restrict_access import restrict_access
from bot.handlers.commands import set_commands
from core import models
from core.config import settings
from core.models.static import Restrictions
from core.schemas.category import CategoryCreate


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if settings.app.super_admin == user_id:
        await set_commands(context.application)

        await context.bot.setMessageReaction(
            update.message.chat_id,
            update.message.message_id,
            reaction=ReactionEmoji.THUMBS_UP
        )