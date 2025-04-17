from datetime import datetime

from pydantic import BaseModel


class ImageBase(BaseModel):
    file_id: str
    local_file_name: str
    description: str | None
    user_id: int

class ImageCreate(ImageBase):
    file_unique_id: str | None


class ImageRead(ImageBase):
    id: int
    file_unique_id: str | None
    is_active: bool
    hidden_by_id: datetime | None
    hidden_at: datetime | None


class ImageUpdate(ImageBase):
    is_active: bool
    hidden_by_id: datetime | None
    hidden_at: datetime | None