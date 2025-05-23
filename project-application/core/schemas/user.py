from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str | None
    telegram_id: int

class UserCreate(UserBase):
    first_name: str | None
    last_name: str | None
    is_deleted: int
    is_admin: int
    can_upload: int
    can_receive: int

class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_deleted: Optional[int] = None
    is_admin: Optional[int] = None
    can_upload: Optional[int] = None
    can_receive: Optional[int] = None


class UserRead(UserBase):
    id: int
    first_name: str | None
    last_name: str | None
    is_deleted: int
    can_upload: int
    is_admin: int
    can_receive: int
    created_at: datetime | None
    updated_at: datetime | None