"""add content column to posts table

Revision ID: fecc1063e386
Revises: 75b7342aad5f
Create Date: 2024-03-15 08:44:18.782041

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fecc1063e386"
down_revision: Union[str, None] = "75b7342aad5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", "content")
    pass
