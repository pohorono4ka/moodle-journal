"""add unique constraint for grade journal rows

Revision ID: 20240314_0002
Revises: 20240314_0001
Create Date: 2024-03-14 00:20:00
"""

from alembic import op


revision = "20240314_0002"
down_revision = "20240314_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_grade_row",
        "grade_records",
        ["student_id", "discipline_id", "graded_at"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_grade_row", "grade_records", type_="unique")
