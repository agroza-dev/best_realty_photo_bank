from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from core.models.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.user import User
    from core.models import Category

class Image(Base):
    file_unique_id: Mapped[str] = mapped_column(String, nullable=True)
    # Нужен для того, чтобы можно было не сохранять оригинал, а дергать сразу с серверов телеги.
    file_id: Mapped[str] = mapped_column(String, nullable=False)

    # Локальный путь к файлу
    local_file_name: Mapped[str] = mapped_column(String, nullable=True)

    # Метки / описание
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # ID сессии добавления
    session_id: Mapped[str] = mapped_column(String, index=True)

    # изображения забронированы пользователем.
    booked_by: Mapped[str] = mapped_column(String, nullable=True)
    # ID сессии бронирования изображений
    booking_session: Mapped[str] = mapped_column(Text, nullable=True)

    # Привязка к пользователю, который добавил фото
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(
        foreign_keys="[Image.user_id]",
        back_populates="images",
    )

    # Дата добавления
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Флаг активности
    is_active: Mapped[bool] = mapped_column(default=True)

    # Кто скрыл (внутренний ID пользователя, скрывшего фото)
    hidden_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    hidden_by: Mapped["User"] = relationship(
        foreign_keys="[Image.hidden_by_id]",
        back_populates="hidden_images",
    )

    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    calculated_hash: Mapped[str] = mapped_column(String, nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", backref=backref("images"))