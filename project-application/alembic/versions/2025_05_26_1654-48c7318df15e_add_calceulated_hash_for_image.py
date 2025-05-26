from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "48c7318df15e"
down_revision: Union[str, None] = "e36a247c3637"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "images", sa.Column("calculated_hash", sa.String(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column("images", "calculated_hash")
