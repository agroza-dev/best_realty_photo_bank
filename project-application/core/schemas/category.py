from typing import Optional

from pydantic import BaseModel

class CategoryBase(BaseModel):
    title: str
    is_active: bool


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    pass


class CategoryUpdate(CategoryBase):
    title: Optional[str]  = None
    is_active: Optional[bool] = None
    pass