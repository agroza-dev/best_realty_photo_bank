import json

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers import set_category_for_upload_session_handler


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = json.loads(query.data)
    if data["act"] == "set_cat":
        await set_category_for_upload_session_handler.handler(update, context)
