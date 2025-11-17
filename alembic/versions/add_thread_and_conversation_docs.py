"""add thread_id and conversation_documents

Revision ID: add_thread_docs_001
Revises: 904dda745ee3
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = 'add_thread_docs_001'
down_revision = '904dda745ee3'
branch_labels = None
depends_on = None


def upgrade():
    # Add thread_id to conversations table
    op.add_column('conversations', sa.Column('thread_id', sa.String(), nullable=True))
    op.create_index('ix_conversations_thread_id', 'conversations', ['thread_id'], unique=True)
    
    # Add conversation_id to documents table
    op.add_column('documents', sa.Column('conversation_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_documents_conversation_id', 'documents', 'conversations', ['conversation_id'], ['id'])
    
    # Create conversation_documents junction table
    op.create_table('conversation_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop conversation_documents table
    op.drop_table('conversation_documents')
    
    # Remove conversation_id from documents
    op.drop_constraint('fk_documents_conversation_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'conversation_id')
    
    # Remove thread_id from conversations
    op.drop_index('ix_conversations_thread_id', table_name='conversations')
    op.drop_column('conversations', 'thread_id')

