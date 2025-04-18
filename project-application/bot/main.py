import httpx
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from core.config import settings

from bot.handlers import start_handler, start_photo_process_handler, receive_image_handler

if __name__ == "__main__":
    request = HTTPXRequest(
        httpx_kwargs={
            "timeout": httpx.Timeout(
                connect = settings.bot.builder.get('connect'),
                read = settings.bot.builder.get('read'),
                write = settings.bot.builder.get('write'),
                pool = settings.bot.builder.get('pool'),
            )
        }
    )

    application = ApplicationBuilder().token(settings.bot.token).request(request).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("add_photos", start_photo_process_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.ATTACHMENT, receive_image_handler))
    application.run_polling()
