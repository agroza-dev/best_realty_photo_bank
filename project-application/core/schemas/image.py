from datetime import datetime

from pydantic import BaseModel


class ImageBase(BaseModel):
    file_unique_id: str
    local_file_name: str
    description: str
    user_id: int

class ImageCreate(ImageBase):
    session_id: str
    file_id: str
    pass


class ImageRead(ImageBase):
    id: int
    is_active: bool
    hidden_by_id: datetime | None
    hidden_at: datetime | None


class ImageUpdate(ImageBase):
    is_active: bool
    hidden_by_id: datetime | None
    hidden_at: datetime | None