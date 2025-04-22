from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Sequence

from core.models import Image
from core.schemas.image import ImageUpdate
from core.schemas.user import UserCreate


async def get_all_images(session: AsyncSession) -> Sequence[Image]:
    statement = select(Image).order_by(Image.id)
    result = await session.scalars(statement)
    return result.all()

async def get_images_by_ids(session: AsyncSession, ids: Sequence[int]) -> Sequence[Image]:
    statement = select(Image).where(Image.id.in_(ids)).order_by(Image.id)
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
    image: Image,
    image_update: ImageUpdate
) -> Image:
    for name, value in image_update.model_dump(exclude_unset=True).items():
        setattr(image, name, value)
    await session.commit()
    return image
