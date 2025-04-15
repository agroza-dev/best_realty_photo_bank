from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import settings

from bot.handlers import start_handler, start_photo_process_handler


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.bot.token).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("add_photos", start_photo_process_handler))
    application.run_polling()
