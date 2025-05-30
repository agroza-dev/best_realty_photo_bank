from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ImageBase(BaseModel):
    file_unique_id: str
    local_file_name: str
    description: str
    user_id: int

class ImageCreate(ImageBase):
    session_id: str
    file_id: str
    calculated_hash: str
    pass


class ImageRead(ImageBase):
    id: int
    is_active: bool
    hidden_by_id: datetime | None
    hidden_at: datetime | None


class ImageUpdate(ImageBase):
    file_unique_id: Optional[str] = None
    local_file_name: Optional[str] = None
    calculated_hash: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    is_active: Optional[bool] = None
    hidden_by_id: Optional[int] = None
    hidden_at: Optional[datetime] = None
    booked_by: Optional[int] = None
    booking_session: Optional[str] = None
    category_id: Optional[int] = None