import secrets
import string

from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.restrict_access import restrict_access, Restrictions
from bot.handlers.helper import reset_user_data
from bot.utils.response import send_response
from utils.templates import render_bot_template
from utils.logger import logger
from bot.utils import state



@restrict_access(Restrictions.upload)
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Starting photo upload process for user: {update.message.from_user.username}")
    context.user_data['states'] = [state.WAITING_FOR_PHOTOS]
    reset_user_data(context)
    await send_response(update, context, response=render_bot_template("add_photos.j2"))
