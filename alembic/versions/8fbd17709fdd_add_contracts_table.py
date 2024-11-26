"""Add contracts table

Revision ID: 8fbd17709fdd
Revises: d43db6bb338f
Create Date: 2024-11-26 06:23:47.944894+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fbd17709fdd'
down_revision: Union[str, None] = 'd43db6bb338f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the `contracts` table
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    # Drop the `contracts` table
    op.drop_table('contracts')
