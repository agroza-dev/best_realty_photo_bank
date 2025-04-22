from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c51fff197b82"
down_revision: Union[str, None] = "a0e8f238caf5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("images", sa.Column("file_id", sa.String(), nullable=False, ))


def downgrade() -> None:
    op.drop_column("images", "file_id")
