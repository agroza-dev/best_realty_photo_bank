from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from telegram import InputMediaPhoto
from telegram import Bot
from api.crud.images import get_all_images, get_images_by_ids
from core import models
from core.config import settings
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
            })
        html_content = render_template('main.j2', {'prepared_images': prepared_images})

        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        # TODO: cлать алярм в sentry или еще куда-то
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing: {str(e)}")


@html_router.post("/select_photos")
async def select_photos(selected_photos_ids: list[str] = Form(...), telegram_user_id: int = Form(...)):
    logger.info(f'Пользователь {telegram_user_id} выбрал фото: {selected_photos_ids}')

    images =  await models.db_helper.execute_with_session(get_images_by_ids, selected_photos_ids)
    paths = []
    for image in images:
        paths.append(f"{settings.images.path}/{image.local_file_name}_original.jpg")

    logger.info(f"Generated paths: {paths}")

    media = [InputMediaPhoto(open(path, 'rb')) for path in paths]

    bot = Bot(token=settings.bot.token)
    await bot.send_media_group(chat_id=telegram_user_id, media=media)

    return RedirectResponse(url="/", status_code=303)

api_router = APIRouter()
