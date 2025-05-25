from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Form, Depends, status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Bot

from api.crud.images import get_all_images, get_images_by_ids, update_image
from bot.utils.files import send_file_as_document
from core import models
from core.config import settings
from core.models import User
from core.schemas.image import ImageUpdate
from utils.logger import logger
from utils.templates import render_web_template
from web_app.dependency.restrict_access import check_can_receive

html_router = APIRouter()

api_router = APIRouter()

@html_router.get("/", response_class=HTMLResponse)
async def read_root(user = Depends(check_can_receive)):
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
        html_content = render_web_template('main/template.j2', {'prepared_images': prepared_images})

        return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)
    except Exception as e:
        # TODO: cлать алярм в sentry или еще куда-то
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing: {str(e)}")

@api_router.post("/select_photos")
async def select_photos(
        selected_photos_ids: Annotated[list[str], Form(...)],
        user = Depends(check_can_receive),
):
    logger.info(f'Пользователь @{user.username}|{user.telegram_id}|{user.first_name} решил забронировать фото: {selected_photos_ids}')

    session_id = uuid4().hex

    images = await models.db_helper.execute_with_session(get_images_by_ids, selected_photos_ids)

    bot = Bot(token=settings.bot.token)
    for image in images:
        image_update = ImageUpdate(booked_by=user.telegram_id, booking_session=session_id)

        await models.db_helper.execute_with_session_scope(update_image, image.id, image_update)
        await send_file_as_document(
            bot=bot,
            chat_id=user.telegram_id,
            file_id=image.file_id,
            filename=f"{image.local_file_name}.jpg"
        )

    await bot.send_message(
        chat_id=user.telegram_id,
        text="Фотографии забронированы, нужно подтвердить действие!",
        reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Подтвердить забор", callback_data=f"confirm_booking_session:{session_id}"),
                InlineKeyboardButton("❌ Отмена бронирования", callback_data=f"reject_booking_session:{session_id}")
            ]
        ])
    )

    return RedirectResponse(url=settings.web_app.url, status_code=status.HTTP_303_SEE_OTHER)

