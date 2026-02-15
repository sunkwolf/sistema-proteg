"""unify_seller_collector_into_employee

Replace separate seller/collector tables with unified employee table.
Add employee_department (M:N) and employee_permission_override.
Migrate existing seller/collector data and update all FK references.

Revision ID: 6524ad295e93
Revises: 1a3018309e6e
Create Date: 2026-02-15 01:53:37.472536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '6524ad295e93'
down_revision: Union[str, None] = '1a3018309e6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Create new tables ──────────────────────────────────────────

    # Employee (replaces seller + collector)
    op.create_table('employee',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('code_name', sa.String(length=50), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('es_vendedor', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('es_cobrador', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('es_ajustador', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('seller_class', postgresql.ENUM('seller', 'collaborator', name='seller_class_type', create_type=False), nullable=True),
        sa.Column('sales_target', sa.Integer(), nullable=True),
        sa.Column('receipt_limit', sa.Integer(), server_default='50', nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'inactive', name='entity_status_type', create_type=False), server_default=sa.text("'active'::entity_status_type"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_name', name='uq_employee_code'),
    )
    op.create_index('idx_employee_status', 'employee', ['status'])
    op.create_index('idx_employee_user', 'employee', ['user_id'])

    # Employee ↔ Department junction
    op.create_table('employee_department',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('es_gerente', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['department.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('employee_id', 'department_id'),
    )

    # Employee permission overrides
    op.create_table('employee_permission_override',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('granted', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'permission_id', name='uq_employee_permission'),
    )

    # ── 2. Migrate data from seller/collector → employee ──────────────
    # Copy sellers as employees with es_vendedor=true
    op.execute("""
        INSERT INTO employee (code_name, full_name, phone, telegram_id,
                              es_vendedor, seller_class, sales_target,
                              status, created_at, updated_at)
        SELECT code_name, full_name, phone, telegram_id,
               true, class, sales_target,
               status, created_at, updated_at
        FROM seller
    """)

    # Copy collectors as employees with es_cobrador=true
    # If a collector has the same code_name as an existing employee (seller),
    # update that employee to also be a cobrador
    op.execute("""
        INSERT INTO employee (code_name, full_name, phone,
                              es_cobrador, receipt_limit,
                              status, created_at, updated_at)
        SELECT c.code_name, c.full_name, c.phone,
               true, c.receipt_limit,
               c.status, c.created_at, c.updated_at
        FROM collector c
        WHERE NOT EXISTS (
            SELECT 1 FROM employee e WHERE e.code_name = c.code_name
        )
    """)

    # For collectors that already exist as sellers, set es_cobrador=true
    op.execute("""
        UPDATE employee e
        SET es_cobrador = true,
            receipt_limit = c.receipt_limit
        FROM collector c
        WHERE e.code_name = c.code_name
    """)

    # ── 3. Update FK references from seller/collector → employee ──────
    # We need to map old seller_id → new employee_id for each FK

    # Policy.seller_id: seller.id → employee.id
    op.execute("""
        UPDATE policy p
        SET seller_id = e.id
        FROM seller s
        JOIN employee e ON e.code_name = s.code_name
        WHERE p.seller_id = s.id
    """)
    op.drop_constraint('policy_seller_id_fkey', 'policy', type_='foreignkey')
    op.create_foreign_key('policy_seller_id_fkey', 'policy', 'employee', ['seller_id'], ['id'], ondelete='SET NULL')

    # Payment.seller_id and Payment.collector_id
    op.execute("""
        UPDATE payment p
        SET seller_id = e.id
        FROM seller s
        JOIN employee e ON e.code_name = s.code_name
        WHERE p.seller_id = s.id
    """)
    op.execute("""
        UPDATE payment p
        SET collector_id = e.id
        FROM collector c
        JOIN employee e ON e.code_name = c.code_name
        WHERE p.collector_id = c.id
    """)
    op.drop_constraint('payment_seller_id_fkey', 'payment', type_='foreignkey')
    op.drop_constraint('payment_collector_id_fkey', 'payment', type_='foreignkey')
    op.create_foreign_key('payment_seller_id_fkey', 'payment', 'employee', ['seller_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('payment_collector_id_fkey', 'payment', 'employee', ['collector_id'], ['id'], ondelete='SET NULL')

    # PaymentProposal.seller_id and PaymentProposal.collector_id
    op.execute("""
        UPDATE payment_proposal pp
        SET seller_id = e.id
        FROM seller s
        JOIN employee e ON e.code_name = s.code_name
        WHERE pp.seller_id = s.id
    """)
    op.execute("""
        UPDATE payment_proposal pp
        SET collector_id = e.id
        FROM collector c
        JOIN employee e ON e.code_name = c.code_name
        WHERE pp.collector_id = c.id
    """)
    op.drop_constraint('payment_proposal_seller_id_fkey', 'payment_proposal', type_='foreignkey')
    op.drop_constraint('payment_proposal_collector_id_fkey', 'payment_proposal', type_='foreignkey')
    op.create_foreign_key('payment_proposal_seller_id_fkey', 'payment_proposal', 'employee', ['seller_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('payment_proposal_collector_id_fkey', 'payment_proposal', 'employee', ['collector_id'], ['id'], ondelete='SET NULL')

    # Card.seller_id
    op.execute("""
        UPDATE card ca
        SET seller_id = e.id
        FROM seller s
        JOIN employee e ON e.code_name = s.code_name
        WHERE ca.seller_id = s.id
    """)
    op.drop_constraint('card_seller_id_fkey', 'card', type_='foreignkey')
    op.create_foreign_key('card_seller_id_fkey', 'card', 'employee', ['seller_id'], ['id'], ondelete='SET NULL')

    # Receipt.collector_id
    op.execute("""
        UPDATE receipt r
        SET collector_id = e.id
        FROM collector c
        JOIN employee e ON e.code_name = c.code_name
        WHERE r.collector_id = c.id
    """)
    op.drop_constraint('receipt_collector_id_fkey', 'receipt', type_='foreignkey')
    op.create_foreign_key('receipt_collector_id_fkey', 'receipt', 'employee', ['collector_id'], ['id'], ondelete='SET NULL')

    # PolicyNotification.seller_id
    op.execute("""
        UPDATE policy_notification pn
        SET seller_id = e.id
        FROM seller s
        JOIN employee e ON e.code_name = s.code_name
        WHERE pn.seller_id = s.id
    """)
    op.drop_constraint('policy_notification_seller_id_fkey', 'policy_notification', type_='foreignkey')
    op.create_foreign_key('policy_notification_seller_id_fkey', 'policy_notification', 'employee', ['seller_id'], ['id'], ondelete='CASCADE')

    # ── 4. Drop old tables ────────────────────────────────────────────
    op.drop_index('idx_seller_status', table_name='seller')
    op.drop_table('seller')
    op.drop_table('collector')


def downgrade() -> None:
    # WARNING: This downgrade is NOT fully reversible.
    # It recreates seller/collector as EMPTY tables and points FKs at them,
    # but does NOT backfill data from employee back to seller/collector.
    # A real rollback requires restoring from backup.
    # Recreate seller and collector tables
    op.create_table('seller',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('code_name', sa.VARCHAR(length=50), nullable=False),
        sa.Column('full_name', sa.VARCHAR(length=255), nullable=False),
        sa.Column('phone', sa.VARCHAR(length=20), nullable=True),
        sa.Column('telegram_id', sa.BIGINT(), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'inactive', name='entity_status_type', create_type=False), server_default=sa.text("'active'::entity_status_type"), nullable=False),
        sa.Column('class', postgresql.ENUM('seller', 'collaborator', name='seller_class_type', create_type=False), server_default=sa.text("'collaborator'::seller_class_type"), nullable=False),
        sa.Column('sales_target', sa.INTEGER(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_name', name='uq_seller_code'),
    )
    op.create_index('idx_seller_status', 'seller', ['status'])

    op.create_table('collector',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('code_name', sa.VARCHAR(length=50), nullable=False),
        sa.Column('full_name', sa.VARCHAR(length=255), nullable=True),
        sa.Column('phone', sa.VARCHAR(length=20), nullable=True),
        sa.Column('receipt_limit', sa.INTEGER(), server_default=sa.text('50'), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'inactive', name='entity_status_type', create_type=False), server_default=sa.text("'active'::entity_status_type"), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_name', name='uq_collector_code'),
    )

    # Revert FKs to point back to seller/collector
    op.drop_constraint('policy_notification_seller_id_fkey', 'policy_notification', type_='foreignkey')
    op.create_foreign_key('policy_notification_seller_id_fkey', 'policy_notification', 'seller', ['seller_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('receipt_collector_id_fkey', 'receipt', type_='foreignkey')
    op.create_foreign_key('receipt_collector_id_fkey', 'receipt', 'collector', ['collector_id'], ['id'], ondelete='SET NULL')

    op.drop_constraint('card_seller_id_fkey', 'card', type_='foreignkey')
    op.create_foreign_key('card_seller_id_fkey', 'card', 'seller', ['seller_id'], ['id'])

    op.drop_constraint('payment_proposal_collector_id_fkey', 'payment_proposal', type_='foreignkey')
    op.drop_constraint('payment_proposal_seller_id_fkey', 'payment_proposal', type_='foreignkey')
    op.create_foreign_key('payment_proposal_seller_id_fkey', 'payment_proposal', 'seller', ['seller_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('payment_proposal_collector_id_fkey', 'payment_proposal', 'collector', ['collector_id'], ['id'], ondelete='SET NULL')

    op.drop_constraint('payment_collector_id_fkey', 'payment', type_='foreignkey')
    op.drop_constraint('payment_seller_id_fkey', 'payment', type_='foreignkey')
    op.create_foreign_key('payment_seller_id_fkey', 'payment', 'seller', ['seller_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('payment_collector_id_fkey', 'payment', 'collector', ['collector_id'], ['id'], ondelete='SET NULL')

    op.drop_constraint('policy_seller_id_fkey', 'policy', type_='foreignkey')
    op.create_foreign_key('policy_seller_id_fkey', 'policy', 'seller', ['seller_id'], ['id'], ondelete='SET NULL')

    # Drop new tables
    op.drop_table('employee_permission_override')
    op.drop_table('employee_department')
    op.drop_table('employee')
