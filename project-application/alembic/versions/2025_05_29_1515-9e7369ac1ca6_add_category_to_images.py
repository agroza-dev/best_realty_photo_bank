from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9e7369ac1ca6"
down_revision: Union[str, None] = "c4a49842eb2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("images", schema=None) as batch_op:
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_images_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
        )

def downgrade() -> None:
    with op.batch_alter_table("images", schema=None) as batch_op:
        batch_op.drop_constraint("fk_images_category_id_categories", type_="foreignkey")
        batch_op.drop_column("category_id")
