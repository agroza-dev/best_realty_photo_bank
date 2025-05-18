from telegram import Update
from telegram.ext import ContextTypes

from api.crud.images import get_images_by_booking_session, update_image
from bot.utils.response import send_response, delete_message
from utils.templates import render_bot_template
from core import models
from core.schemas.image import ImageUpdate


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    booking_session = query.data.split(":")[1]

    images = await models.db_helper.execute_with_session(get_images_by_booking_session, booking_session)
    for image in images:
        image_update = ImageUpdate(booked_by=None, booking_session=None)
        await models.db_helper.execute_with_session_scope(update_image, image.id, image_update)

    await delete_message(update.effective_message.message_id, update, context)

    await send_response(update, context, response=render_bot_template("reject_booking_session.j2"))
