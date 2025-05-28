from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4a49842eb2f"
down_revision: Union[str, None] = "274db1b6d92a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "categories", sa.Column("is_active", sa.Boolean(), nullable=False)
    )

def downgrade() -> None:
    op.drop_column("categories", "is_active")
