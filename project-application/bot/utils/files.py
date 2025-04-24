import io

from telegram import Bot, InputFile
from telegram.constants import ChatAction
from telegram.error import TelegramError


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
        print(f"[!] Ошибка при отправке файла: {e}")