from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Form, Depends, status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Bot

from api.crud.categories import get_categories, CategoryFilter
from api.crud.filter import FieldFilter
from api.crud.images import get_images_by_ids, update_image, ImageFilter, get_images
from bot.utils.files import send_file_as_document
from core import models
from core.config import settings
from core.schemas.image import ImageUpdate
from utils.logger import logger
from utils.templates import render_web_template
from web_app.dependency.restrict_access import check_can_receive

html_router = APIRouter()

api_router = APIRouter()

@html_router.get("/", response_class=HTMLResponse)
async def read_root(category_id: int | None = None, user = Depends(check_can_receive)):
    images_filter = ImageFilter(category_id=FieldFilter(is_null=True), is_active=FieldFilter(eq=1))
    print(category_id)
    if category_id is not None and category_id:
        images_filter = ImageFilter(category_id=FieldFilter(eq=int(category_id)), is_active=FieldFilter(eq=1))

    try:
        images = await models.db_helper.execute_with_session(get_images, images_filter)
        prepared_images = []

        for image in images:
            prepared_images.append({
                'id': image.id,
                'path': f"images/{image.local_file_name}_thumb.jpg",
                'description': image.description,
                'added_by': image.user.username,
                'is_booked': image.booked_by is not None,
            })

        html_content = render_web_template('main/template.j2', {
                'prepared_images': prepared_images,
                'categories': await models.db_helper.execute_with_session(get_categories, CategoryFilter()),
                'category_id': category_id,
            }
        )

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
    booked = 0
    for image in images:
        try:
            image_update = ImageUpdate(booked_by=user.telegram_id, booking_session=session_id)

            await models.db_helper.execute_with_session_scope(update_image, image.id, image_update)
            await send_file_as_document(
                bot=bot,
                chat_id=user.telegram_id,
                file_id=image.file_id,
                filename=f"{image.local_file_name}.jpg"
            )
            booked += 1
        except Exception as e:
            print(f"[!] Ошибка при отправке файла {image.id}: {e}")

    if booked > 0:
        await bot.send_message(
            chat_id=user.telegram_id,
            text="Фотографии забронированы, нужно подтвердить действие!",
            reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Подтвердить забор", callback_data=f"confirm_booking_session:{session_id}"),
                    InlineKeyboardButton("❌ Отмена бронирования", callback_data=f"reject_booking_session:{session_id}")
                ]
            ])
        )
    else:
        await bot.send_message(
            chat_id=user.telegram_id,
            text="Ошибка! С этими фотографиями возникла проблема, не могу выдать их",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Скрыть проблемные фото", callback_data=f"confirm_booking_session:{session_id}"),
            ]
            ])
        )

    return RedirectResponse(url=settings.web_app.url, status_code=status.HTTP_303_SEE_OTHER)

