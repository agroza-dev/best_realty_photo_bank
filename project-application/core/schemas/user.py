from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str | None
    telegram_id: int

class UserCreate(UserBase):
    first_name: str | None
    last_name: str | None


class UserRead(UserBase):
    id: int
    first_name: str | None
    last_name: str | None
    is_deleted: int
    created_at: datetime | None
    updated_at: datetime | None