from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Sequence

from sqlalchemy.orm import selectinload

from core.models import Image
from core.schemas.image import ImageUpdate
from core.schemas.user import UserCreate


async def get_all_images(session: AsyncSession) -> Sequence[Image]:
    statement = (
        select(Image)
        .where(Image.is_active == 1)
        .options(selectinload(Image.user))
        .order_by(Image.id))
    result = await session.scalars(statement)
    return result.all()

async def get_images_by_ids(session: AsyncSession, ids: Sequence[int]) -> Sequence[Image]:
    statement = (
        select(Image)
        .where(Image.id.in_(ids))
        .options(selectinload(Image.user))
        .order_by(Image.id)
    )
    result = await session.scalars(statement)
    return result.all()

async def get_images_by_booking_session(session: AsyncSession, booking_session: str) -> Sequence[Image]:
    statement = (
        select(Image)
        .where(Image.booking_session == booking_session)
        .options(selectinload(Image.user))
        .order_by(Image.id)
    )
    result = await session.scalars(statement)
    return result.all()

async def create_image(
    session: AsyncSession,
    image_create: UserCreate,
) -> Image:
    image = Image(**image_create.model_dump())
    session.add(image)
    await session.commit()
    return image


async def update_image(
    session: AsyncSession,
    image_id: int,
    image_update: ImageUpdate
) -> Image:
    image = await session.get(Image, image_id)
    if image is None:
        raise ValueError(f"Image with id {image_id} not found")

    for name, value in image_update.model_dump(exclude_unset=True).items():
        setattr(image, name, value)

    await session.commit()
    await session.refresh(image)
    return image
