from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import AcademicYear, AttendanceStatus, Course, Discipline, GradeType, Group, LessonType, Semester, Student

router = APIRouter(prefix="/reference-data", tags=["reference_data"])


@router.get("/academic-years")
def list_academic_years(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(AcademicYear).all()


@router.get("/semesters")
def list_semesters(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Semester).all()


@router.get("/courses")
def list_courses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Course).all()


@router.get("/groups")
def list_groups(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Group).all()


@router.get("/disciplines")
def list_disciplines(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Discipline).all()


@router.get("/lesson-types")
def list_lesson_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(LessonType).all()


@router.get("/attendance-statuses")
def list_attendance_statuses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(AttendanceStatus).all()


@router.get("/grade-types")
def list_grade_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(GradeType).all()


@router.get("/students")
def list_students(group_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Student).filter(Student.group_id == group_id).order_by(Student.full_name.asc()).all()
