from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e36a247c3637"
down_revision: Union[str, None] = "1ceb1de8a9f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
