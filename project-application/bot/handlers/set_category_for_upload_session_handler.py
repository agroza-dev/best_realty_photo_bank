import json
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from api.crud.categories import get_category, CategoryFilter
from api.crud.filter import FieldFilter
from api.crud.images import get_images_by_booking_session, update_image, ImageFilter, get_images
from bot.decorators.restrict_access import restrict_access, Restrictions
from bot.handlers.helper import reset_user_data
from bot.utils.response import send_response, delete_message
from utils.logger import logger
from utils.templates import render_bot_template
from core import models
from core.schemas.image import ImageUpdate

@restrict_access(Restrictions.upload)
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = json.loads(query.data)
    category_id = data["cid"]
    session_id = data["sid"]

    category = await models.db_helper.execute_with_session(get_category, CategoryFilter(id=FieldFilter(eq=category_id)))

    images = await models.db_helper.execute_with_session(get_images, ImageFilter(session_id=FieldFilter(eq=session_id)))
    if not images:
        logger.error(f'Не удалось получить фотки для сессии {session_id}')
        raise ValueError("Ошибка. Не найдены фотографии для данной сессии")

    for image in images:
        await models.db_helper.execute_with_session_scope(update_image, image.id, ImageUpdate(category_id=category_id))

    try:
        await delete_message(update.effective_message.message_id, update, context)

        await send_response(
            update,
            context,
            response=render_bot_template(
                "confirm_category_apply_for_images.j2",
                {"category_title": category.title, "images_count": len(images), "description": image.description},
            )
        )
    except Exception as e:
        logger.error(f"[set_category_for_upload_session] Не удалось подтвердить применение категории для сессии {session_id} err {e}")
        raise ValueError("Ошибка. Не удалось отправить подтверждение действия.")
    finally:
        reset_user_data(context)