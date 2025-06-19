from telegram import  BotCommand, BotCommandScopeChat
from telegram.ext import Application

from api.crud.users import get_user_by_tg_id, get_all_users
from core import models

from core.models import db_helper, User


async def set_user_specific_commands(app: Application, user_id: int) -> None:
    bot = app.bot
    user: User = await db_helper.execute_with_session(get_user_by_tg_id, user_id)

    if user is None:
        return

    commands = [
        BotCommand(command="start", description="Запустить/Перезапустить бота"),
    ]

    if not user.is_deleted:
        commands.append(BotCommand(command="show", description="Показать кнопку webapp"))

        if user.can_upload:
            commands.append(BotCommand(command="add_photos", description="Добавить фотографии"))

        if user.is_admin:
            commands.append(BotCommand(command="manage_users", description="Изменять роли пользователей"))
            commands.append(BotCommand(command="refresh_commands_list", description="Пере применить список команд"))

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeChat(chat_id=user_id)
    )


async def set_commands(app: Application) -> None:
    users = await models.db_helper.execute_with_session(get_all_users)

    for user in users:
        await set_user_specific_commands(app, user.telegram_id)