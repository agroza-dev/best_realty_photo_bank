from typing import Literal, Union

from fastapi import APIRouter, HTTPException, Depends, status, Path, Body
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from api.crud.users import get_all_users, get_user_by_tg_id, update_user
from bot.decorators.restrict_access import Restrictions
from core import models
from core.models import db_helper
from core.schemas.user import UserUpdate
from utils.logger import logger
from utils.templates import render_web_template
from web_app.dependency.restrict_access import check_is_admin

html_router = APIRouter()

api_router = APIRouter()

@html_router.get("/manage_users", response_class=HTMLResponse)
async def read_users(user = Depends(check_is_admin)):
    try:
        users = await models.db_helper.execute_with_session(get_all_users)
        html_content = render_web_template('users/template.j2', {"users_list": users, "current_user": user.id})
        return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"undefined_error")


class UserUpdateParams(BaseModel):
    flag: str
    value: Union[bool, int]

@api_router.patch("/edit_user/{user_tg_id}")
async def change_user_flag(
    user_tg_id: int = Path(...),
    payload: UserUpdateParams = Body(...),
    current_user=Depends(check_is_admin),
):
    target_user = await db_helper.execute_with_session(get_user_by_tg_id, user_tg_id)

    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found_in_database")

    # Обновляем нужное поле
    if payload.flag == Restrictions.upload:
        user_update = UserUpdate(can_upload=bool(payload.value))
    elif payload.flag == Restrictions.receive:
        user_update = UserUpdate(can_receive=bool(payload.value))
    elif payload.flag == Restrictions.is_deleted:
        user_update = UserUpdate(is_deleted=bool(payload.value))
    elif payload.flag == Restrictions.is_admin:
        user_update = UserUpdate(is_admin=bool(payload.value))
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect_data")

    updated_user = await models.db_helper.execute_with_session_scope(update_user, target_user.id, user_update)

    return JSONResponse(
        content={"message": f"Флаг '{payload.flag}' обновлён для пользователя '{updated_user.username}'", "value": payload.value},
        status_code=200
    )
