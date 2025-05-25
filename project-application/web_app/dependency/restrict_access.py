import hashlib
import hmac
import json
import urllib.parse
from fastapi import HTTPException, Depends, status, Request
from typing import Annotated

from api.crud.users import get_user_by_tg_id
from core.config import settings
from core.models import User, db_helper
from utils.logger import logger


async def get_init_data(request: Request) -> str:
    if "initData" in request.query_params:
        return request.query_params["initData"]

    form = await request.form()
    if "init_data" in form:
        return form["init_data"]
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="incomplete_init_user_data")


def validate_telegram_init_data(init_data: str) -> dict:
    auth_data, hash_str = parse_init_data(init_data)

    bot_token = settings.bot.token

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(auth_data.items()))
    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_user_hash")
    return auth_data


async def get_valid_user(init_data: Annotated[str, Depends(get_init_data)]) -> User:
    auth_data = validate_telegram_init_data(init_data)

    try:
        user_data = json.loads(auth_data.get("user", "{}"))
        user_id = user_data["id"]
    except (KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid_user_data")

    user = await db_helper.execute_with_session(get_user_by_tg_id, user_id)

    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="access_denied")

    return user


def parse_init_data(init_data: str) -> tuple[dict[str, str], str]:
    data_list = [chunk.split("=", 1) for chunk in urllib.parse.unquote(init_data).split("&")]
    auth_data = {key: value for key, value in data_list if key != "hash"}
    hash_str = next((value for key, value in data_list if key == "hash"), None)
    if not hash_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="incomplete_init_user_data")
    return auth_data, hash_str


def check_can_upload(user: Annotated[User, Depends(get_valid_user)]) -> User:
    if not user.can_upload:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="upload_permission_denied")
    return user


def check_can_receive(user: Annotated[User, Depends(get_valid_user)]) -> User:
    if not user.can_receive:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="receive_permission_denied")
    return user


def check_is_admin(user: Annotated[User, Depends(get_valid_user)]) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user_is_not_admin")
    return user
