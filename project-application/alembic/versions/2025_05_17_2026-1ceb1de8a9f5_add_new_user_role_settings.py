
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "1ceb1de8a9f5"
down_revision: Union[str, None] = "db4121f8040d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "can_upload",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "can_receive",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "can_receive")
    op.drop_column("users", "can_upload")