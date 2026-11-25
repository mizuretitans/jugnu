"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-11-25 14:57:26.619293
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table('users',
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('auth_subject', sa.Uuid(), nullable=True),
    sa.Column('email', sa.String(length=320), nullable=True),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(name) <> ''", name=op.f('ck_users_name_not_blank')),
    sa.CheckConstraint("role IN ('student', 'mentor')", name=op.f('ck_users_role')),
    sa.CheckConstraint('email = lower(email)', name=op.f('ck_users_email_lower')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('auth_subject', name=op.f('uq_users_auth_subject'))
    )
    op.create_table('community_posts',
    sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('field', sa.String(length=20), nullable=False),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.Column('body', sa.String(length=1500), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(body) <> ''", name=op.f('ck_community_posts_body_not_blank')),
    sa.CheckConstraint("field IN ('civil_services', 'defense', 'teaching', 'technology', 'undecided')", name=op.f('ck_community_posts_field')),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_community_posts_author_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_community_posts'))
    )
    op.create_index(op.f('ix_community_posts_field_id'), 'community_posts', ['field', 'id'], unique=False)
    op.create_table('helper_messages',
    sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("role IN ('user', 'assistant')", name=op.f('ck_helper_messages_role')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_helper_messages_user_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_helper_messages'))
    )
    op.create_index(op.f('ix_helper_messages_user_id_id'), 'helper_messages', ['user_id', 'id'], unique=False)
    op.create_table('intake_messages',
    sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("role IN ('user', 'assistant')", name=op.f('ck_intake_messages_role')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_intake_messages_user_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_intake_messages'))
    )
    op.create_index(op.f('ix_intake_messages_user_id_id'), 'intake_messages', ['user_id', 'id'], unique=False)
    op.create_table('intake_profiles',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=20), server_default='in_progress', nullable=False),
    sa.Column('phase_turns', sa.Integer(), server_default='0', nullable=False),
    sa.Column('route_failures', sa.Integer(), server_default='0', nullable=False),
    sa.Column('profile', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('primary_field', sa.String(length=20), nullable=True),
    sa.Column('analysis', postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), nullable=True),
    sa.Column('needs_human_followup', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('busy_token', sa.Uuid(), nullable=True),
    sa.Column('busy_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("primary_field IN ('civil_services', 'defense', 'teaching', 'technology', 'medical', 'business', 'creative', 'undecided')", name=op.f('ck_intake_profiles_primary_field')),
    sa.CheckConstraint("status IN ('in_progress', 'confirming', 'ready_to_route', 'completed')", name=op.f('ck_intake_profiles_status')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_intake_profiles_user_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', name=op.f('pk_intake_profiles'))
    )
    op.create_index('ix_intake_profiles_followup', 'intake_profiles', ['updated_at'], unique=False, postgresql_where=sa.text('needs_human_followup'))
    op.create_table('mentor_profiles',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('field', sa.String(length=20), nullable=False),
    sa.Column('bio', sa.String(length=500), nullable=False),
    sa.Column('hourly_rate_paise', sa.Integer(), nullable=False),
    sa.Column('is_listed', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.CheckConstraint("field IN ('civil_services', 'defense', 'teaching', 'technology', 'medical', 'business', 'creative')", name=op.f('ck_mentor_profiles_field')),
    sa.CheckConstraint('hourly_rate_paise BETWEEN 100 AND 10000000 AND mod(hourly_rate_paise, 100) = 0', name=op.f('ck_mentor_profiles_rate_whole_rupees')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_mentor_profiles_user_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', name=op.f('pk_mentor_profiles'))
    )
    op.create_index(op.f('ix_mentor_profiles_field'), 'mentor_profiles', ['field'], unique=False)
    op.create_table('mentorship_requests',
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('mentor_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=10), server_default='pending', nullable=False),
    sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(status = 'accepted') = (accepted_at IS NOT NULL)", name=op.f('ck_mentorship_requests_accepted_at')),
    sa.CheckConstraint("status IN ('pending', 'accepted')", name=op.f('ck_mentorship_requests_status')),
    sa.ForeignKeyConstraint(['mentor_id'], ['users.id'], name=op.f('fk_mentorship_requests_mentor_id'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_mentorship_requests_student_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_mentorship_requests')),
    sa.UniqueConstraint('student_id', 'mentor_id', name=op.f('uq_mentorship_requests_student_id_mentor_id'))
    )
    op.create_index(op.f('ix_mentorship_requests_mentor_id_status'), 'mentorship_requests', ['mentor_id', 'status'], unique=False)
    op.create_table('bookings',
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('idempotency_key', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('mentor_id', sa.Uuid(), nullable=False),
    sa.Column('request_id', sa.Uuid(), nullable=True),
    sa.Column('hourly_rate_paise', sa.Integer(), nullable=False),
    sa.Column('minutes', sa.Integer(), nullable=False),
    sa.Column('total_paise', sa.Integer(), nullable=False),
    sa.Column('topic', sa.String(length=300), nullable=False),
    sa.Column('status', sa.String(length=10), server_default='pending', nullable=False),
    sa.Column('payment_mode', sa.String(length=10), server_default='simulated', nullable=False),
    sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(status = 'confirmed') = (request_id IS NOT NULL AND confirmed_at IS NOT NULL)", name=op.f('ck_bookings_confirmed')),
    sa.CheckConstraint("payment_mode = 'simulated'", name=op.f('ck_bookings_payment_mode')),
    sa.CheckConstraint("status IN ('pending', 'confirmed')", name=op.f('ck_bookings_status')),
    sa.CheckConstraint('minutes IN (30, 60, 90, 120)', name=op.f('ck_bookings_minutes')),
    sa.CheckConstraint('total_paise::bigint * 60 = hourly_rate_paise::bigint * minutes', name=op.f('ck_bookings_total')),
    sa.ForeignKeyConstraint(['mentor_id'], ['users.id'], name=op.f('fk_bookings_mentor_id'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['request_id'], ['mentorship_requests.id'], name=op.f('fk_bookings_request_id')),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_bookings_student_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bookings')),
    sa.UniqueConstraint('student_id', 'idempotency_key', name=op.f('uq_bookings_student_id_idempotency_key'))
    )
    op.create_index(op.f('ix_bookings_mentor_id_created_at'), 'bookings', ['mentor_id', 'created_at'], unique=False)
    op.create_table('conversation_messages',
    sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('request_id', sa.Uuid(), nullable=False),
    sa.Column('sender_id', sa.Uuid(), nullable=False),
    sa.Column('body', sa.String(length=1500), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("btrim(body) <> ''", name=op.f('ck_conversation_messages_body_not_blank')),
    sa.ForeignKeyConstraint(['request_id'], ['mentorship_requests.id'], name=op.f('fk_conversation_messages_request_id'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], name=op.f('fk_conversation_messages_sender_id'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_conversation_messages'))
    )
    op.create_index(op.f('ix_conversation_messages_request_id_id'), 'conversation_messages', ['request_id', 'id'], unique=False)



def downgrade() -> None:

    op.drop_index(op.f('ix_conversation_messages_request_id_id'), table_name='conversation_messages')
    op.drop_table('conversation_messages')
    op.drop_index(op.f('ix_bookings_mentor_id_created_at'), table_name='bookings')
    op.drop_table('bookings')
    op.drop_index(op.f('ix_mentorship_requests_mentor_id_status'), table_name='mentorship_requests')
    op.drop_table('mentorship_requests')
    op.drop_index(op.f('ix_mentor_profiles_field'), table_name='mentor_profiles')
    op.drop_table('mentor_profiles')
    op.drop_index('ix_intake_profiles_followup', table_name='intake_profiles', postgresql_where=sa.text('needs_human_followup'))
    op.drop_table('intake_profiles')
    op.drop_index(op.f('ix_intake_messages_user_id_id'), table_name='intake_messages')
    op.drop_table('intake_messages')
    op.drop_index(op.f('ix_helper_messages_user_id_id'), table_name='helper_messages')
    op.drop_table('helper_messages')
    op.drop_index(op.f('ix_community_posts_field_id'), table_name='community_posts')
    op.drop_table('community_posts')
    op.drop_table('users')

