import hashlib
import hmac
import json
import urllib.parse
from fastapi import Form, HTTPException, Depends, status
from typing import Annotated

from api.crud.users import get_user_by_tg_id
from core.config import settings
from core.models import User, db_helper


class InvalidAuthData(Exception):
    pass


def parse_init_data(init_data: str) -> tuple[dict[str, str], str]:
    data_list = [chunk.split("=", 1) for chunk in urllib.parse.unquote(init_data).split("&")]
    auth_data = {key: value for key, value in data_list if key != "hash"}
    hash_str = next((value for key, value in data_list if key == "hash"), None)
    if not hash_str:
        raise InvalidAuthData("Hash not found in initData.")
    return auth_data, hash_str


def verify_data_hash(auth_data: dict[str, str], hash_str: str, bot_token: str):
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(auth_data.items()))
    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_str:
        raise InvalidAuthData("Invalid hash")


def validate_telegram_init_data(init_data: Annotated[str, Form(...)]) -> dict:
    auth_data, hash_str = parse_init_data(init_data)
    verify_data_hash(auth_data, hash_str, settings.bot.token)
    return auth_data


async def get_current_user(
    auth_data: Annotated[dict, Depends(validate_telegram_init_data)]
) -> User:
    try:
        user_info = json.loads(auth_data.get("user", "{}"))
        user_id = user_info.get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found")

        user = await db_helper.execute_with_session(get_user_by_tg_id, user_id)
        if user is None or user.is_deleted:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return user

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid user JSON")


def check_can_upload(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.can_upload:
        raise HTTPException(status_code=403, detail="Upload permission denied")
    return user


def check_can_receive(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.can_receive:
        raise HTTPException(status_code=403, detail="Receive permission denied")
    return user