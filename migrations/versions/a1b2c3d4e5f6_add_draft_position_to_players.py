"""add draft_position to players

Revision ID: a1b2c3d4e5f6
Revises: 319dcfae4f6f
Create Date: 2026-05-17 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "319dcfae4f6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "players",
        sa.Column("draft_position", sa.Integer(), nullable=True),
        schema="nba",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("players", "draft_position", schema="nba")
