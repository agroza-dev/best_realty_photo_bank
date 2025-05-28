import io
import hashlib
import os
from io import BytesIO
from typing import Union

from telegram import Bot, InputFile, Message, PhotoSize, Document
from telegram._bot import BT
from telegram.constants import ChatAction
from telegram.error import TelegramError
from dataclasses import dataclass

from api.crud.images import ImageFilter, FieldFilter, get_images
from core import models
from utils.logger import logger
from PIL import Image

@dataclass
class CreatedImage:
    file_unique_id: str
    file_id: str
    local_file_name: str

async def send_file_as_document(bot: Bot, chat_id: int, file_id: str, filename: str = "file.jpg"):
    try:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)

        file = await bot.get_file(file_id)
        buffer = io.BytesIO()
        await file.download_to_memory(out=buffer)
        buffer.seek(0)

        await bot.send_document(
            chat_id=chat_id,
            document=InputFile(buffer, filename=filename),
        )
    except TelegramError as e:
        logger.error(f"[!] Ошибка при отправке файла: {e}")
        raise ValueError("Ошибка. Не удалось выдать забронированное изображение.")

TARGET_THUMB_SIZE = (320, 320)

def get_original_file(message: Message):
    if message.photo:
        return message.photo[-1]
    if message.document:
        return message.document

def calculate_image_hash(file_bytes):
    """Вычисляем SHA256 хеш для изображения."""
    file_bytes.seek(0)
    return hashlib.sha256(file_bytes.read()).hexdigest()

async def is_hash_already_exists(file_hash):
    filters = ImageFilter(
        calculated_hash=FieldFilter(eq=file_hash),
    )
    images = await models.db_helper.execute_with_session(get_images, filters)
    if images:
        return True
    return False

def get_safe_filename(filename: str) -> str:
    return filename.strip().replace(" ", "_").rstrip("-.")


async def download_and_resize(bot: BT, file: PhotoSize, name: str, save_dir: str):
    thumb_path = os.path.join(save_dir, f"{name}_thumb.jpg")
    telegram_file = await bot.get_file(file.file_id)

    file_bytes = BytesIO()
    await telegram_file.download_to_memory(out=file_bytes)

    # Вернём курсор снова в начало перед открытием PIL
    file_bytes.seek(0)
    image = Image.open(file_bytes)
    image = image.resize(TARGET_THUMB_SIZE, Image.Resampling.LANCZOS)
    image.save(thumb_path, "JPEG")


async def get_hash(bot: BT, file: Union[PhotoSize, Document]) -> str:
    telegram_file = await bot.get_file(file.file_id)

    file_bytes = BytesIO()
    await telegram_file.download_to_memory(out=file_bytes)

    # Вернём курсор в начало перед чтением
    file_bytes.seek(0)

    # Вычисляем хеш по байтам изображения
    return calculate_image_hash(file_bytes)


async def save_telegram_image(bot: BT, message: Message, save_dir: str) -> CreatedImage:
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"Try to save image from message: {message}")

    if message.photo:
        photo_sizes = sorted(message.photo, key=lambda p: p.width)
        original = photo_sizes[-1]
        thumbnail = photo_sizes[1] if len(photo_sizes) > 2 else photo_sizes[0]

        local_file_name = get_safe_filename(thumbnail.file_unique_id)

        await download_and_resize(bot, thumbnail, local_file_name, save_dir)

        return CreatedImage(
            file_unique_id=original.file_unique_id,
            file_id=original.file_id,
            local_file_name=local_file_name,
        )

    elif message.document and message.document.mime_type.startswith("image/"):
        doc = message.document
        if doc.thumbnail:
            local_file_name = get_safe_filename(doc.thumbnail.file_unique_id)
            await download_and_resize(bot, doc.thumbnail, local_file_name, save_dir)

            return CreatedImage(
                file_unique_id=doc.file_unique_id,
                file_id=doc.file_id,
                local_file_name=local_file_name,
            )
    else:
        raise ValueError("Message does not contain a valid image.")