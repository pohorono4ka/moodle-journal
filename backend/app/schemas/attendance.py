from datetime import date
from pydantic import BaseModel, Field


class AttendanceUpsert(BaseModel):
    student_id: int
    discipline_id: int
    lesson_date: date
    lesson_type_id: int
    status_id: int
    comment: str | None = None


class AttendanceBulkPresent(BaseModel):
    student_ids: list[int]
    discipline_id: int
    lesson_date: date
    lesson_type_id: int
    present_status_id: int


class AttendanceView(BaseModel):
    id: int
    student_id: int
    status_id: int
    lesson_date: date


class JournalSelectionQuery(BaseModel):
    academic_year_id: int
    semester_id: int
    study_form: str
    course_id: int
    group_id: int
    discipline_id: int
    lesson_date: date
    lesson_type_id: int = 1


class StudentAttendanceRow(BaseModel):
    student_id: int
    full_name: str
    attendance_record_id: int | None
    status_id: int | None


class AttendanceJournalResponse(BaseModel):
    filters: JournalSelectionQuery
    students: list[StudentAttendanceRow]


class AttendanceSaveItem(BaseModel):
    student_id: int
    status_id: int = Field(..., description="Attendance status id")


class AttendanceJournalSaveRequest(BaseModel):
    discipline_id: int
    lesson_date: date
    lesson_type_id: int
    items: list[AttendanceSaveItem]
