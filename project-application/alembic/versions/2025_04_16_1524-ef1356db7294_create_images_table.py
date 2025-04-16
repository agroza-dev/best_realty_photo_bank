from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ef1356db7294"
down_revision: Union[str, None] = "422752e32a2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("file_id", sa.String(), nullable=False),
        sa.Column("file_unique_id", sa.String(), nullable=True),
        sa.Column("local_file_name", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("hidden_by_id", sa.Integer(), nullable=True),
        sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["hidden_by_id"],
            ["users.id"],
            name=op.f("fk_images_hidden_by_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_images_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_images")),
    )
    op.create_index(
        op.f("ix_images_session_id"), "images", ["session_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_images_session_id"), table_name="images")
    op.drop_table("images")
