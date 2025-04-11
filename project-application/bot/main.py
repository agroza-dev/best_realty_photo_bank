from telegram.ext import ApplicationBuilder, CommandHandler
from core.config import settings

from bot.handlers import start_handler


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.bot.token).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.run_polling()
