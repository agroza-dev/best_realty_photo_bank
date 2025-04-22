import os
from dataclasses import dataclass

from uuid import uuid4

from telegram import Update, Message
from telegram._bot import BT
from telegram.ext import ContextTypes

from api.crud.images import create_image
from api.crud.users import get_user_by_tg_id
from bot.handlers.helper import do_with_retry
from bot.utils.response import send_response, delete_message
from bot.utils.templates import render_template
from core import models
from core.schemas.image import ImageCreate
from utils.logger import logger
from bot import state
from core.config import settings
from PIL import Image
from telegram.error import TimedOut


@dataclass
class CreatedImage:
    original: str
    thumbnail: str
    file_unique_id: str


async def before_process(context: ContextTypes.DEFAULT_TYPE, update: Update):
    message_media_group_id = update.message.media_group_id
    context.user_data['session_media_group'] = message_media_group_id

    last_message_id = context.user_data.get('last_message_id', False)
    logger.info(f"last_message_id = {last_message_id}")
    if last_message_id is not False:
        logger.info(f"Try to delete message: {last_message_id}")
        try:
            await delete_message(update, last_message_id)
        except TimedOut:
            logger.warning(f"Timed out while deleting message: {last_message_id}")

    sent_message = False
    try:
        sent_message = await send_response(
            update,
            context,
            response=render_template("receive_image.j2", {'status': 'in_progress'})
        )
        logger.info(f"Sent message {sent_message}")
        context.user_data['last_message_id'] = sent_message.message_id
    except TimedOut:
        logger.warning(f"Timed out while sending message: {sent_message}")


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    user = await models.db_helper.execute_with_session(get_user_by_tg_id, message.from_user.id)
    if user is None:
        logger.warning(f"User {message.from_user.id} not found")
        await send_response(
            update,
            context,
            response=render_template("receive_image.j2", {'status': 'user_not_found'})
        )
        return None

    logger.info(f"receive_images_handler user_data: {context.user_data} from user: {user}")
    allowed_states = [state.WAITING_FOR_PHOTOS, state.WAITING_FOR_TAGS]
    current_states = context.user_data.get('states', state.EMPTY)

    if not any(element in allowed_states for element in current_states):
        logger.info(f"State does not match. Expected : {allowed_states} got {current_states}")
        await send_response(
            update,
            context,
            response=render_template("receive_image.j2", {'status': 'wrong_state'})
        )
        return

    logger.info(f"receive_image_handler message: {message}")
    if message.photo or message.document:
        message_media_group_id = message.media_group_id
        session_media_group_id = context.user_data.get('session_media_group', False)
        logger.info(f"MEDIA GROUP: message -> {message_media_group_id}    session -> {session_media_group_id}")
        if not session_media_group_id or session_media_group_id != message_media_group_id:
            await before_process(context, update)
        logger.info(f"Context data after_before process: {context.user_data}")

        img_name = uuid4().hex
        created_image = await save_telegram_image(context.bot, message, settings.images.path, img_name)
        session_image_count = context.user_data.get('session_image_count', 0)
        context.user_data['session_image_count'] =  session_image_count + 1

        if message.caption:
            context.user_data['session_message'] = message.caption

        new_image_create = ImageCreate(
            file_unique_id=created_image.file_unique_id,
            local_file_name=img_name,
            user_id=user.id,
            session_id=context.user_data.get('session'),
            description=context.user_data.get('session_message') or '',
        )
        new_image: models.Image = await models.db_helper.execute_with_session_scope(create_image, new_image_create)
        if new_image is not None:
            logger.info(f"Created image {new_image}")
        else:
            logger.error(f"Error on create image {new_image_create} => {message.from_user.username}")
            # TODO: Send error message?

        response_message = render_template(
            "receive_image.j2",
            {'status': 'images_was_received', 'session_image_count': context.user_data.get('session_image_count', 0)}
        )

        last_message_id = context.user_data.get('last_message_id', None)
        logger.info(f"last_message_id = {last_message_id}")
        if last_message_id is not None:
            logger.info(f"debug {response_message} {update.effective_chat} {context.user_data.get('last_message_id')}")
            await context.bot.edit_message_text(response_message, update.effective_chat.id, context.user_data.get('last_message_id'))
        else:
            sent_message = await send_response(update, context, response=response_message)
            logger.info(f"Sent message {sent_message}")
            context.user_data['last_message_id'] = sent_message.message_id


async def save_telegram_image(bot: BT, message: Message, save_dir: str, prefix: str) -> CreatedImage:
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f" try to save image from message: {message}")

    if message.photo:
        photo_sizes = sorted(message.photo, key=lambda p: p.width)
        original = photo_sizes[-1]
        thumbnail = photo_sizes[1] if len(photo_sizes) > 2 else photo_sizes[0]

        logger.info(f"Original: {original}")
        logger.info(f"Thumbnail: {thumbnail}")

        orig_path = os.path.join(save_dir, f"{prefix}_original.jpg")
        thumb_path = os.path.join(save_dir, f"{prefix}_thumb.jpg")

        await do_with_retry((await bot.get_file(original.file_id)).download_to_drive,  orig_path, label='original')
        await do_with_retry((await bot.get_file(thumbnail.file_id)).download_to_drive,  thumb_path, label='thumbnail')

        return CreatedImage(
            original=orig_path,
            thumbnail=thumb_path,
            file_unique_id=original.file_unique_id
        )

    elif message.document and message.document.mime_type.startswith("image/"):
        doc = message.document
        mime_type = message.document.mime_type if message.document else None

        is_jpeg = mime_type == "image/jpeg"

        orig_path = os.path.join(save_dir, f"{prefix}_original.jpg")
        temp_path = os.path.join(save_dir, f"{prefix}_original_temp")
        await (await bot.get_file(message.document.file_id)).download_to_drive(temp_path)

        if is_jpeg:
            os.rename(temp_path, orig_path)
        else:
            with Image.open(temp_path) as img:
                img.convert("RGB").save(orig_path, "JPEG", quality=90)
            os.remove(temp_path)


        if doc.thumbnail:
            thumb_path = os.path.join(save_dir, f"{prefix}_thumb.jpg")
            await (await bot.get_file(doc.thumbnail.file_id)).download_to_drive(thumb_path)
        else:
            thumb_path = None

        return CreatedImage(
            original=orig_path,
            thumbnail=thumb_path,
            file_unique_id=doc.file_unique_id
        )
    else:
        raise ValueError("Message does not contain a valid image.")