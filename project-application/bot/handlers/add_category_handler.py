from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import ContextTypes

from api.crud.categories import CategoryFilter, get_category, create_category
from api.crud.filter import FieldFilter
from core import models
from core.config import settings
from core.schemas.category import CategoryCreate


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args
    if not args[0]:
        return
    category_name = args[0]

    if settings.app.super_admin == user_id:
        filters = CategoryFilter(title=FieldFilter(eq=category_name))

        category = await models.db_helper.execute_with_session(get_category, filters)
        if category is None:
            category_create = CategoryCreate(title=category_name, is_active=True)
            created_category = await models.db_helper.execute_with_session_scope(create_category, category_create)
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