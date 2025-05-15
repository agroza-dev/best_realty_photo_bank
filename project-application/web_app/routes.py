import io
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from telegram import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram import Bot
from telegram.constants import ChatAction
from telegram.error import TelegramError

from api.crud.images import get_all_images, get_images_by_ids, update_image
from bot.utils.files import send_file_as_document
from core import models
from core.config import settings
from core.schemas.image import ImageUpdate
from utils.logger import logger
from web_app.utils.templates import render_template

# Создаем роутер для HTML страниц
html_router = APIRouter()


@html_router.get("/", response_class=HTMLResponse)
async def read_root():
    try:

        images = await models.db_helper.execute_with_session(get_all_images)
        prepared_images = []

        for image in images:
            prepared_images.append({
                'id': image.id,
                'path': f"images/{image.local_file_name}_thumb.jpg",
                'description': image.description,
                'added_by': image.user.username,
                'is_booked': image.booked_by is not None,
            })
        html_content = render_template('main.j2', {'prepared_images': prepared_images})

        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        # TODO: cлать алярм в sentry или еще куда-то
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing: {str(e)}")


api_router = APIRouter()
@api_router.post("/select_photos")
async def select_photos(selected_photos_ids: list[str] = Form(...), telegram_user_id: int = Form(...)):
    logger.info(f'Пользователь {telegram_user_id} решил забронировать фото: {selected_photos_ids}')

    session_id = uuid4().hex

    images = await models.db_helper.execute_with_session(get_images_by_ids, selected_photos_ids)

    bot = Bot(token=settings.bot.token)
    for image in images:
        image_update = ImageUpdate(booked_by=telegram_user_id, booking_session=session_id)

        await models.db_helper.execute_with_session_scope(update_image, image.id, image_update)
        await send_file_as_document(
            bot=bot,
            chat_id=telegram_user_id,
            file_id=image.file_id,
            filename=f"{image.local_file_name}.jpg"
        )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Подтвердить забор", callback_data=f"confirm_booking_session:{session_id}"),
            InlineKeyboardButton("❌ Отмена бронирования", callback_data=f"reject_booking_session:{session_id}")
        ]
    ])

    await bot.send_message(
        chat_id=telegram_user_id,
        text="Фотографии забронированы, нужно подтвердить действие!",
        reply_markup=keyboard
    )

    return RedirectResponse(url="/", status_code=303)

