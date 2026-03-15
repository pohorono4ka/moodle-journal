"""init schema

Revision ID: 20240314_0001
Revises: 
Create Date: 2024-03-14 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20240314_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.Enum("teacher", "head_of_department", "dean_office", "admin", name="userrole"), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table("user_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    op.create_table("academic_years", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(20), unique=True), sa.Column("is_active", sa.Boolean(), server_default=sa.true()))
    op.create_table("semesters", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(30), unique=True))
    op.create_table("courses", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("number", sa.Integer(), nullable=False))
    op.create_table("disciplines", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(255), nullable=False))
    op.create_table("lesson_types", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), unique=True))
    op.create_table("grade_types", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), unique=True))

    op.create_table("groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), unique=True),
        sa.Column("study_form", sa.Enum("full_time", "part_time", name="studyform"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id"), nullable=False),
    )
    op.create_table("students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("moodle_id", sa.Integer(), unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
    )
    op.create_table("teacher_discipline_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("discipline_id", sa.Integer(), sa.ForeignKey("disciplines.id"), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
    )
    op.create_table("attendance_statuses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.Enum("present", "absent", "excused", "late", name="attendancestatuscode"), unique=True, nullable=False),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
    )

    op.create_table("attendance_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("discipline_id", sa.Integer(), sa.ForeignKey("disciplines.id"), nullable=False),
        sa.Column("lesson_date", sa.Date(), nullable=False),
        sa.Column("lesson_type_id", sa.Integer(), sa.ForeignKey("lesson_types.id"), nullable=False),
        sa.Column("status_id", sa.Integer(), sa.ForeignKey("attendance_statuses.id"), nullable=False),
        sa.Column("comment", sa.String(255)),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("student_id", "discipline_id", "lesson_date", "lesson_type_id", name="uq_attendance_row"),
    )

    op.create_table("grade_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("discipline_id", sa.Integer(), sa.ForeignKey("disciplines.id"), nullable=False),
        sa.Column("grade_type_id", sa.Integer(), sa.ForeignKey("grade_types.id"), nullable=False),
        sa.Column("value", sa.Numeric(4, 2), nullable=False),
        sa.Column("graded_at", sa.Date(), nullable=False),
        sa.Column("comment", sa.String(255)),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table("audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_name", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text()),
        sa.Column("new_value", sa.Text()),
        sa.Column("changed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_entity_name", "audit_logs", ["entity_name"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_entity_name", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("grade_records")
    op.drop_table("attendance_records")
    op.drop_table("attendance_statuses")
    op.drop_table("teacher_discipline_groups")
    op.drop_table("students")
    op.drop_table("groups")
    op.drop_table("grade_types")
    op.drop_table("lesson_types")
    op.drop_table("disciplines")
    op.drop_table("courses")
    op.drop_table("semesters")
    op.drop_table("academic_years")
    op.drop_table("user_roles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("roles")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS studyform")
    op.execute("DROP TYPE IF EXISTS attendancestatuscode")
