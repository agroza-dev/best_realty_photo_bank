from telegram import Update, InlineKeyboardButton, WebAppInfo, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.decorators.restrict_access import Restrictions, restrict_access
from core.config import settings

@restrict_access(Restrictions.is_admin)
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Пользователи",
                web_app=WebAppInfo(url=settings.web_app.users_url)
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Открыть',
        reply_markup=reply_markup
    )