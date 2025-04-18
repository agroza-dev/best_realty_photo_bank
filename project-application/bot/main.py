import httpx
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from core.config import settings

from bot.handlers import start_handler, start_photo_process_handler


if __name__ == "__main__":
    request = HTTPXRequest(
        httpx_kwargs={
            "timeout": httpx.Timeout(
                connect=3.0,
                read=10.0,
                write=10.0,
                pool=2.0,
            )
        }
    )

    application = ApplicationBuilder().token(settings.bot.token).request(request).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("add_photos", start_photo_process_handler))
    application.run_polling()
