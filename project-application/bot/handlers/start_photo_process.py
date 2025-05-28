from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.restrict_access import restrict_access, Restrictions
from bot.utils.response import send_response
from utils.templates import render_bot_template
from utils.logger import logger
from bot.utils import state
from uuid import uuid4


@restrict_access(Restrictions.upload)
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Starting photo upload process for user: {update.message.from_user.username}")
    context.user_data['states'] = [state.WAITING_FOR_PHOTOS]
    context.user_data['session'] = str(uuid4())
    context.user_data['session_image_duplicate_count'] = 0
    context.user_data['session_image_count'] = 0
    context.user_data['session_message'] = False
    await send_response(update, context, response=render_bot_template("add_photos.j2"))
