from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "db4121f8040d"
down_revision: Union[str, None] = "c51fff197b82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("images", sa.Column("booked_by", sa.String(), nullable=True))
    op.add_column(
        "images", sa.Column("booking_session", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_images_user_id_users"), "images", type_="foreignkey"
    )
    op.create_foreign_key(None, "images", "users", ["user_id"], ["id"])
    op.drop_column("images", "booking_session")
    op.drop_column("images", "booked_by")
