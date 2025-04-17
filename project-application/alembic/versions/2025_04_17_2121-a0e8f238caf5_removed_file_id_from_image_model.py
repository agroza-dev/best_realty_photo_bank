from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a0e8f238caf5"
down_revision: Union[str, None] = "ef1356db7294"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("images", "file_id")


def downgrade() -> None:
    op.add_column("images", sa.Column("file_id", sa.VARCHAR(), nullable=False))
