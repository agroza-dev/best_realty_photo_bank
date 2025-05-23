from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, DateTime, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy import func, text

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.image import Image

from core.models.base import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        server_onupdate=func.now(),
    )
    images: Mapped[list["Image"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Image.user_id]"
    )
    hidden_images: Mapped[list["Image"]] = relationship(
        back_populates="hidden_by", viewonly=True,
        foreign_keys="[Image.hidden_by_id]",
    )
    can_upload: Mapped[bool] = mapped_column(Integer, default=1, server_default=text("1"))
    can_receive: Mapped[bool] = mapped_column(Integer, default=1, server_default=text("1"))
    is_admin: Mapped[bool] = mapped_column(Integer, default=0, server_default=text("0"))


    def __repr__(self) -> str:
        return f"<User tg_id={self.telegram_id} username={self.username}>"
