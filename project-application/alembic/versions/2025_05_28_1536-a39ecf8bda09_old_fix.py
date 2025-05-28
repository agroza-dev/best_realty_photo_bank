from typing import Sequence, Union

from alembic import op

revision: str = "a39ecf8bda09"
down_revision: Union[str, None] = "48c7318df15e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(None, "images", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_images_user_id_users"),
        "images",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_images_user_id_users"), "images", type_="foreignkey"
    )
    op.create_foreign_key(None, "images", "users", ["user_id"], ["id"])
