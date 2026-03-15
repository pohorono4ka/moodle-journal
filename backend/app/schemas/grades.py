from datetime import date

from pydantic import BaseModel


class GradeUpsert(BaseModel):
    student_id: int
    discipline_id: int
    grade_type_id: int
    value: float
    graded_at: date
    comment: str | None = None


class GradeView(BaseModel):
    id: int
    student_id: int
    discipline_id: int
    grade_type_id: int
    value: float


class GradeJournalSelectionQuery(BaseModel):
    academic_year_id: int
    semester_id: int
    study_form: str
    course_id: int
    group_id: int
    discipline_id: int
    graded_at: date


class StudentGradeRow(BaseModel):
    student_id: int
    full_name: str
    grade_record_id: int | None
    grade_type_id: int | None
    value: float | None


class GradeJournalResponse(BaseModel):
    filters: GradeJournalSelectionQuery
    students: list[StudentGradeRow]


class GradeSaveItem(BaseModel):
    student_id: int
    grade_type_id: int
    value: float


class GradeJournalSaveRequest(BaseModel):
    discipline_id: int
    graded_at: date
    items: list[GradeSaveItem]
