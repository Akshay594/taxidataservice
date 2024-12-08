# scripts/db_migrations/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from src.config.settings import settings
from src.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.Engine,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# scripts/db_migrations/versions/001_initial_tables.py
"""initial tables

Revision ID: 001
Revises: 
Create Date: 2024-12-08
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create taxi_trips table
    op.create_table(
        'taxi_trips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.String(), nullable=True),
        sa.Column('pickup_datetime', sa.DateTime(), nullable=True),
        sa.Column('dropoff_datetime', sa.DateTime(), nullable=True),
        sa.Column('pickup_hour', sa.Integer(), nullable=True),
        sa.Column('pickup_day', sa.String(), nullable=True),
        sa.Column('pickup_month', sa.Integer(), nullable=True),
        sa.Column('is_rush_hour', sa.Boolean(), nullable=True),
        sa.Column('is_weekend', sa.Boolean(), nullable=True),
        sa.Column('time_category', sa.String(), nullable=True),
        sa.Column('pickup_latitude', sa.Float(), nullable=True),
        sa.Column('pickup_longitude', sa.Float(), nullable=True),
        sa.Column('dropoff_latitude', sa.Float(), nullable=True),
        sa.Column('dropoff_longitude', sa.Float(), nullable=True),
        sa.Column('trip_distance', sa.Float(), nullable=True),
        sa.Column('passenger_count', sa.Integer(), nullable=True),
        sa.Column('trip_duration', sa.Integer(), nullable=True),
        sa.Column('average_speed', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_taxi_trips_id', 'taxi_trips', ['id'])
    op.create_index('ix_taxi_trips_pickup_datetime', 'taxi_trips', ['pickup_datetime'])
    
    # Create trip_aggregations table
    op.create_table(
        'trip_aggregations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('hour', sa.Integer(), nullable=True),
        sa.Column('total_trips', sa.Integer(), nullable=True),
        sa.Column('average_duration', sa.Float(), nullable=True),
        sa.Column('average_distance', sa.Float(), nullable=True),
        sa.Column('average_passengers', sa.Float(), nullable=True),
        sa.Column('total_passengers', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_trip_aggregations_date', 'trip_aggregations', ['date'])

def downgrade() -> None:
    op.drop_index('ix_trip_aggregations_date', 'trip_aggregations')
    op.drop_table('trip_aggregations')
    op.drop_index('ix_taxi_trips_pickup_datetime', 'taxi_trips')
    op.drop_index('ix_taxi_trips_id', 'taxi_trips')
    op.drop_table('taxi_trips')