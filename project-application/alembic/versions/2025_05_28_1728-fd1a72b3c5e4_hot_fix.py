from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "fd1a72b3c5e4"
down_revision: Union[str, None] = "48c7318df15e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создание новой таблицы без ON DELETE CASCADE
    op.execute("""
        CREATE TABLE images_new (
            id              INTEGER PRIMARY KEY,
            file_unique_id  VARCHAR,
            local_file_name VARCHAR,
            description     TEXT,
            session_id      VARCHAR NOT NULL,
            user_id         INTEGER NOT NULL,
            added_at        DATETIME NOT NULL,
            is_active       BOOLEAN NOT NULL,
            hidden_by_id    INTEGER,
            hidden_at       DATETIME,
            file_id         VARCHAR NOT NULL,
            booked_by       VARCHAR,
            booking_session TEXT,
            calculated_hash VARCHAR,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(hidden_by_id) REFERENCES users(id)
        );
    """)

    # 2. Копирование данных
    op.execute("""
        INSERT INTO images_new (
            id, file_unique_id, local_file_name, description, session_id,
            user_id, added_at, is_active, hidden_by_id, hidden_at,
            file_id, booked_by, booking_session, calculated_hash
        )
        SELECT
            id, file_unique_id, local_file_name, description, session_id,
            user_id, added_at, is_active, hidden_by_id, hidden_at,
            file_id, booked_by, booking_session, calculated_hash
        FROM images;
    """)

    # 3. Удаление старой таблицы
    op.drop_table("images")

    # 4. Переименование новой таблицы
    op.rename_table("images_new", "images")

    # 5. Восстановление индексов
    op.create_index("ix_images_session_id", "images", ["session_id"])


def downgrade() -> None:
    # 1. Создание таблицы с ON DELETE CASCADE
    op.execute("""
        CREATE TABLE images_old (
            id              INTEGER PRIMARY KEY,
            file_unique_id  VARCHAR,
            local_file_name VARCHAR,
            description     TEXT,
            session_id      VARCHAR NOT NULL,
            user_id         INTEGER NOT NULL,
            added_at        DATETIME NOT NULL,
            is_active       BOOLEAN NOT NULL,
            hidden_by_id    INTEGER,
            hidden_at       DATETIME,
            file_id         VARCHAR NOT NULL,
            booked_by       VARCHAR,
            booking_session TEXT,
            calculated_hash VARCHAR,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(hidden_by_id) REFERENCES users(id)
        );
    """)

    # 2. Копирование данных обратно
    op.execute("""
        INSERT INTO images_old (
            id, file_unique_id, local_file_name, description, session_id,
            user_id, added_at, is_active, hidden_by_id, hidden_at,
            file_id, booked_by, booking_session, calculated_hash
        )
        SELECT
            id, file_unique_id, local_file_name, description, session_id,
            user_id, added_at, is_active, hidden_by_id, hidden_at,
            file_id, booked_by, booking_session, calculated_hash
        FROM images;
    """)

    # 3. Удаление текущей таблицы
    op.drop_table("images")

    # 4. Переименование обратно
    op.rename_table("images_old", "images")

    # 5. Восстановление индекса
    op.create_index("ix_images_session_id", "images", ["session_id"])
