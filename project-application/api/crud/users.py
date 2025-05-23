from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Sequence

from core.models import User
from core.schemas.user import UserCreate


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    statement = select(User).order_by(User.id)
    result = await session.scalars(statement)
    return result.all()

async def get_user_by_tg_id(
        session: AsyncSession,
        tg_id: int
) -> User:
    statement = select(User).where(User.telegram_id == tg_id)
    result = await session.scalars(statement)
    return result.first()

async def create_user(
    session: AsyncSession,
    user_create: UserCreate,
) -> User:
    user = User(**user_create.model_dump())
    session.add(user)
    await session.commit()
    return user

async def update_user(
    session: AsyncSession,
    user_id: int,
    user_update: UserUpdate
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise ValueError(f"User with id {user_id} not found")
    for name, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, name, value)

    await session.commit()
    await session.refresh(user)
    return user