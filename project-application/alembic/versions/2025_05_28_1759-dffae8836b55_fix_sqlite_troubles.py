
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "dffae8836b55"
down_revision: Union[str, None] = "fd1a72b3c5e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
