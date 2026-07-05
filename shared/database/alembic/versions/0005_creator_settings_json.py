"""add creator_profiles.settings_json

Revision ID: 0005_creator_settings_json
Revises: 0004_user_password_hash
Create Date: 2026-07-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_creator_settings_json"
down_revision: Union[str, None] = "0004_user_password_hash"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("creator_profiles", sa.Column("settings_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("creator_profiles", "settings_json")
