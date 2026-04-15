"""Add bookings table

Revision ID: 001
Revises: 
Create Date: 2025-01-11 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bookings table
    op.create_table('bookings',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('booking_date', sa.Date(), nullable=False),
        sa.Column('booking_time', sa.Time(), nullable=False),
        sa.Column('guests_count', sa.Integer(), nullable=False),
        sa.Column('contact_name', sa.String(200), nullable=False),
        sa.Column('contact_phone', sa.String(20), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on booking_date for faster queries
    op.create_index('ix_bookings_booking_date', 'bookings', ['booking_date'])
    
    # Create index on status for filtering
    op.create_index('ix_bookings_status', 'bookings', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_bookings_status', table_name='bookings')
    op.drop_index('ix_bookings_booking_date', table_name='bookings')
    
    # Drop table
    op.drop_table('bookings')


