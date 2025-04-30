import httpx
from telegram import BotCommand, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, Application, PicklePersistence
from telegram.request import HTTPXRequest

from core.config import settings

from bot.handlers import start_handler, start_photo_process_handler, receive_image_handler, show_webapp_handler, \
    confirm_booking_session_handler, reject_booking_session_handler

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


    async def set_commands(app: Application):
        bot: Bot = app.bot  # Подчеркивает потому, что bot - это @cached_property(создается на лету), но почему-то явно не описан в Application.
        await bot.set_my_commands([
            BotCommand(command="start", description="Запустить/Перезапустить бота"),
            BotCommand(command="add_photos", description="Включить режим добавления фотографий"),
            BotCommand(command="show", description="Показать кнопку webapp"),
        ])

    persistence = PicklePersistence(filepath=settings.db.persistence)

    application = (ApplicationBuilder()
                   .token(settings.bot.token)
                   .request(request)
                   .post_init(set_commands)
                   .persistence(persistence)
                   .build()
    )
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("add_photos", start_photo_process_handler))
    application.add_handler(CommandHandler("show", show_webapp_handler))
    application.add_handler(MessageHandler(filters.PHOTO | filters.ATTACHMENT, receive_image_handler))
    application.add_handler(CallbackQueryHandler(confirm_booking_session_handler, pattern=r"^confirm_booking_session:"))
    application.add_handler(CallbackQueryHandler(reject_booking_session_handler, pattern=r"^reject_booking_session:"))


    application.run_polling()
