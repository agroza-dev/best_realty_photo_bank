from telegram import Update
from telegram.ext import ContextTypes

from api.crud.images import create_image
from api.crud.users import get_user_by_tg_id
from bot.decorators.restrict_access import restrict_access, Restrictions
from bot.utils.files import save_telegram_image, get_hash, is_hash_already_exists, get_original_file
from bot.utils.response import send_response, delete_message
from utils.templates import render_bot_template
from core import models
from core.schemas.image import ImageCreate
from utils.logger import logger
from bot.utils import state
from core.config import settings

from telegram.error import TimedOut


async def before_process(context: ContextTypes.DEFAULT_TYPE, update: Update):
    message_media_group_id = update.message.media_group_id
    context.user_data['session_media_group'] = message_media_group_id

    last_message_id = context.user_data.get('last_message_id', False)
    logger.info(f"last_message_id = {last_message_id}")
    if last_message_id is not False:
        logger.info(f"Try to delete message: {last_message_id}")
        try:
            await delete_message(last_message_id, update, context)
        except TimedOut:
            logger.warning(f"Timed out while deleting message: {last_message_id}")

    sent_message = False
    try:
        sent_message = await send_response(
            update,
            context,
            response=render_bot_template("receive_image.j2", {'status': 'in_progress'})
        )
        logger.info(f"Sent message {sent_message}")
        context.user_data['last_message_id'] = sent_message.message_id
    except TimedOut:
        logger.warning(f"Timed out while sending message: {sent_message}")

@restrict_access(Restrictions.upload)
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    user = await models.db_helper.execute_with_session(get_user_by_tg_id, message.from_user.id)
    if user is None:
        logger.warning(f"User {message.from_user.id} not found")
        await send_response(
            update,
            context,
            response=render_bot_template("receive_image.j2", {'status': 'user_not_found'})
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
            response=render_bot_template("receive_image.j2", {'status': 'wrong_state'})
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


        file_hash = await get_hash(context.bot, get_original_file(message))

        if await is_hash_already_exists(file_hash):
            """Фотография с таким hash уже есть"""
            session_image_duplicate_count = context.user_data.get('session_image_duplicate_count', 0)
            context.user_data['session_image_duplicate_count'] = session_image_duplicate_count + 1
        else:
            created_image = await save_telegram_image(context.bot, message, settings.images.path)
            session_image_count = context.user_data.get('session_image_count', 0)
            context.user_data['session_image_count'] =  session_image_count + 1

            if message.caption:
                context.user_data['session_message'] = message.caption

            new_image_create = ImageCreate(
                file_unique_id=created_image.file_unique_id,
                file_id=created_image.file_id,
                local_file_name=created_image.local_file_name,
                user_id=user.id,
                session_id=context.user_data.get('session'),
                description=context.user_data.get('session_message') or '',
                calculated_hash=file_hash,
            )
            new_image: models.Image = await models.db_helper.execute_with_session_scope(create_image, new_image_create)
            if new_image is not None:
                logger.info(f"Created image {new_image}")
            else:
                logger.error(f"Error on create image {new_image_create} => {message.from_user.username}")
                # TODO: Send error message?

        response_message = render_bot_template("receive_image.j2",{
                'status': 'images_was_received',
                'session_image_count': context.user_data.get('session_image_count', 0),
                'session_image_duplicate_count': context.user_data.get('session_image_duplicate_count', 0),
            }
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
