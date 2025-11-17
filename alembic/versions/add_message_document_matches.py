"""add message document matches table

Revision ID: message_doc_matches_001
Revises: add_thread_docs_001
Create Date: 2025-11-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'message_doc_matches_001'
down_revision: Union[str, None] = 'add_thread_docs_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create message_document_matches table
    op.create_table(
        'message_document_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('matched_content', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_document_matches_id'), 'message_document_matches', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_message_document_matches_id'), table_name='message_document_matches')
    op.drop_table('message_document_matches')
