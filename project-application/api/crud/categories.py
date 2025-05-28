from typing import Sequence, Optional

from pydantic import BaseModel
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.filter import FieldFilter, apply_filter
from core.models import Category
from core.schemas.category import CategoryCreate
from utils.logger import logger


class CategoryFilter(BaseModel):
    id: Optional[FieldFilter[int]] = None
    title: Optional[FieldFilter[str]] = None
    is_active: Optional[FieldFilter[bool]] = None


def build_statement(filters: CategoryFilter) ->  Select[tuple[Category]]:
    stmt = select(Category)

    if filters.id:
        stmt = stmt.where(*apply_filter(Category.id, filters.id))
    if filters.title:
        stmt = stmt.where(*apply_filter(Category.title, filters.title))
    if filters.is_active:
        stmt = stmt.where(*apply_filter(Category.is_active, filters.is_active))

    return stmt


async def get_categories(session: AsyncSession, filters: CategoryFilter) -> Sequence[Category]:
    try:
        stmt = build_statement(filters)
        result = await session.scalars(stmt)
        return result.all()
    except Exception as e:
        logger.exception(f"[get_categories] Необработанное исключение: {e}, для фильтра {filters}")
        raise


async def get_category(session: AsyncSession, filters: CategoryFilter) -> Category:
    try:
        stmt = build_statement(filters)

        stmt = stmt.order_by(Category.id)
        result = await session.scalars(stmt)
        return result.first()
    except Exception as e:
        logger.exception(f"[get_category] Необработанное исключение: {e}, для фильтра {filters}")
        raise



async def create_category(
    session: AsyncSession,
    category_create: CategoryCreate,
) -> Category:
    category = Category(**category_create.model_dump())
    session.add(category)
    await session.commit()
    return category