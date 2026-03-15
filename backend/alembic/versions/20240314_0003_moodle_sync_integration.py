"""moodle sync integration tables and external ids

Revision ID: 20240314_0003
Revises: 20240314_0002
Create Date: 2024-03-14 00:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20240314_0003"
down_revision = "20240314_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("moodle_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_users_moodle_id", "users", ["moodle_id"])

    op.add_column("courses", sa.Column("moodle_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_courses_moodle_id", "courses", ["moodle_id"])

    op.add_column("groups", sa.Column("moodle_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_groups_moodle_id", "groups", ["moodle_id"])

    op.add_column("disciplines", sa.Column("moodle_id", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_disciplines_moodle_id", "disciplines", ["moodle_id"])

    op.create_unique_constraint(
        "uq_teacher_discipline_group",
        "teacher_discipline_groups",
        ["teacher_id", "discipline_id", "group_id"],
    )

    op.create_table(
        "moodle_sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("triggered_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.Enum("success", "failed", "partial", name="syncstatus"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
    )

    op.create_table(
        "moodle_sync_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("moodle_sync_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_name", sa.String(length=100), nullable=False),
        sa.Column("processed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Text(), nullable=True),
    )
    op.create_index("ix_moodle_sync_logs_run_id", "moodle_sync_logs", ["run_id"])
    op.create_index("ix_moodle_sync_logs_entity_name", "moodle_sync_logs", ["entity_name"])


def downgrade() -> None:
    op.drop_index("ix_moodle_sync_logs_entity_name", table_name="moodle_sync_logs")
    op.drop_index("ix_moodle_sync_logs_run_id", table_name="moodle_sync_logs")
    op.drop_table("moodle_sync_logs")
    op.drop_table("moodle_sync_runs")
    op.execute("DROP TYPE IF EXISTS syncstatus")

    op.drop_constraint("uq_teacher_discipline_group", "teacher_discipline_groups", type_="unique")

    op.drop_constraint("uq_disciplines_moodle_id", "disciplines", type_="unique")
    op.drop_column("disciplines", "moodle_id")

    op.drop_constraint("uq_groups_moodle_id", "groups", type_="unique")
    op.drop_column("groups", "moodle_id")

    op.drop_constraint("uq_courses_moodle_id", "courses", type_="unique")
    op.drop_column("courses", "moodle_id")

    op.drop_constraint("uq_users_moodle_id", "users", type_="unique")
    op.drop_column("users", "moodle_id")
