from typing import AsyncGenerator, Callable, TypeVar, Awaitable, Generic
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from core.config import settings


T = TypeVar('T')


class DatabaseHelper(Generic[T]):
    def __init__(
            self,
            url: str,
            echo: bool = False,
            echo_pool: bool = False,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def execute_with_session(
            self,
            func: Callable[..., Awaitable[T]],
            *args,
            **kwargs
    ) -> T:
        async with self.session_factory() as session:
            return await func(session, *args, **kwargs)

    async def execute_with_session_scope(
            self,
            func: Callable[..., Awaitable[T]],
            *args,
            **kwargs
    ) -> T:
        async with self.session_factory() as session:
            try:
                result = await func(session, *args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e


db_helper = DatabaseHelper(
    url=str(settings.db.dsn),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
)
