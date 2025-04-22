from telegram import Update, InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Открыть webapp",
                web_app=WebAppInfo(url=settings.web_app.URL)
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Нажмите на кнопку, чтобы выбрать фотографии.',
        reply_markup=reply_markup
    )