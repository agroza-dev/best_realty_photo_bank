from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "274db1b6d92a"
down_revision: Union[str, None] = "dffae8836b55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("title", name=op.f("uq_categories_title")),
    )

def downgrade() -> None:
    op.drop_table("categories")
