from telegram import Update, InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.decorators.restrict_access import restrict_access, Restrictions
from core.config import settings

@restrict_access(Restrictions.receive)
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Открыть webapp",
                web_app=WebAppInfo(url=settings.web_app.url)
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Нажмите на кнопку, чтобы выбрать фотографии.',
        reply_markup=reply_markup
    )