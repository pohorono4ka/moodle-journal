import enum
from datetime import datetime, date

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    teacher = "teacher"
    head_of_department = "head_of_department"
    dean_office = "dean_office"
    admin = "admin"


class StudyForm(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"


class AttendanceStatusCode(str, enum.Enum):
    present = "present"
    absent = "absent"
    excused = "excused"
    late = "late"


class SyncStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    partial = "partial"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    moodle_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    roles: Mapped[list["Role"]] = relationship(secondary="user_roles", back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[UserRole] = mapped_column(Enum(UserRole), unique=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    users: Mapped[list[User]] = relationship(secondary="user_roles", back_populates="roles")


class UserRoleLink(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    moodle_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    number: Mapped[int] = mapped_column(Integer)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    moodle_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    study_form: Mapped[StudyForm] = mapped_column(Enum(StudyForm))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))


class Discipline(Base):
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(primary_key=True)
    moodle_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    moodle_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))


class TeacherDisciplineGroup(Base):
    __tablename__ = "teacher_discipline_groups"
    __table_args__ = (UniqueConstraint("teacher_id", "discipline_id", "group_id", name="uq_teacher_discipline_group"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))


class LessonType(Base):
    __tablename__ = "lesson_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class AttendanceStatus(Base):
    __tablename__ = "attendance_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[AttendanceStatusCode] = mapped_column(Enum(AttendanceStatusCode), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("student_id", "discipline_id", "lesson_date", "lesson_type_id", name="uq_attendance_row"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"))
    lesson_date: Mapped[date] = mapped_column(Date)
    lesson_type_id: Mapped[int] = mapped_column(ForeignKey("lesson_types.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("attendance_statuses.id"))
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GradeType(Base):
    __tablename__ = "grade_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class GradeRecord(Base):
    __tablename__ = "grade_records"
    __table_args__ = (
        UniqueConstraint("student_id", "discipline_id", "graded_at", name="uq_grade_row"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"))
    grade_type_id: Mapped[int] = mapped_column(ForeignKey("grade_types.id"))
    value: Mapped[float] = mapped_column(Numeric(4, 2))
    graded_at: Mapped[date] = mapped_column(Date)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MoodleSyncRun(Base):
    __tablename__ = "moodle_sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    triggered_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String(20), default="demo")
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus), default=SyncStatus.success)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class MoodleSyncLog(Base):
    __tablename__ = "moodle_sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("moodle_sync_runs.id", ondelete="CASCADE"), index=True)
    entity_name: Mapped[str] = mapped_column(String(100), index=True)
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_name: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[int] = mapped_column(Integer)
    field_name: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
