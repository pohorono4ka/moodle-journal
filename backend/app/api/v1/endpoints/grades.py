from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import GradeRecord, Group, Student, User
from app.schemas.grades import GradeJournalResponse, GradeJournalSaveRequest, GradeJournalSelectionQuery, GradeUpsert, StudentGradeRow
from app.services.audit import write_audit_log

router = APIRouter(prefix="/grades", tags=["grades"])


@router.get("/")
def list_grades(discipline_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(GradeRecord).filter(GradeRecord.discipline_id == discipline_id).all()


@router.get("/journal", response_model=GradeJournalResponse)
def get_grade_journal(
    academic_year_id: int = Query(...),
    semester_id: int = Query(...),
    study_form: str = Query(...),
    course_id: int = Query(...),
    group_id: int = Query(...),
    discipline_id: int = Query(...),
    graded_at: date = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    group = (
        db.query(Group)
        .filter(
            Group.id == group_id,
            Group.course_id == course_id,
            Group.study_form == study_form,
        )
        .first()
    )
    if not group:
        return GradeJournalResponse(
            filters=GradeJournalSelectionQuery(
                academic_year_id=academic_year_id,
                semester_id=semester_id,
                study_form=study_form,
                course_id=course_id,
                group_id=group_id,
                discipline_id=discipline_id,
                graded_at=graded_at,
            ),
            students=[],
        )

    students = db.query(Student).filter(Student.group_id == group.id).order_by(Student.full_name.asc()).all()
    student_ids = [student.id for student in students]

    existing = (
        db.query(GradeRecord)
        .filter(
            GradeRecord.discipline_id == discipline_id,
            GradeRecord.graded_at == graded_at,
            GradeRecord.student_id.in_(student_ids) if student_ids else False,
        )
        .all()
    )
    existing_map = {record.student_id: record for record in existing}

    rows = [
        StudentGradeRow(
            student_id=student.id,
            full_name=student.full_name,
            grade_record_id=existing_map.get(student.id).id if existing_map.get(student.id) else None,
            grade_type_id=existing_map.get(student.id).grade_type_id if existing_map.get(student.id) else None,
            value=float(existing_map.get(student.id).value) if existing_map.get(student.id) else None,
        )
        for student in students
    ]

    return GradeJournalResponse(
        filters=GradeJournalSelectionQuery(
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            study_form=study_form,
            course_id=course_id,
            group_id=group_id,
            discipline_id=discipline_id,
            graded_at=graded_at,
        ),
        students=rows,
    )


@router.post("/journal/save")
def save_grade_journal(payload: GradeJournalSaveRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    updated = 0
    for item in payload.items:
        row = (
            db.query(GradeRecord)
            .filter(
                GradeRecord.student_id == item.student_id,
                GradeRecord.discipline_id == payload.discipline_id,
                GradeRecord.graded_at == payload.graded_at,
            )
            .first()
        )

        if row:
            old_value = str(row.value)
            row.value = item.value
            row.grade_type_id = item.grade_type_id
            row.updated_by = user.id
        else:
            old_value = None
            row = GradeRecord(
                student_id=item.student_id,
                discipline_id=payload.discipline_id,
                grade_type_id=item.grade_type_id,
                value=item.value,
                graded_at=payload.graded_at,
                updated_by=user.id,
            )
            db.add(row)

        db.flush()
        write_audit_log(
            db,
            entity_name="grade_records",
            entity_id=row.id,
            field_name="value",
            old_value=old_value,
            new_value=str(item.value),
            changed_by=user.id,
        )
        updated += 1

    db.commit()
    return {"updated": updated}


@router.post("/")
def create_grade(payload: GradeUpsert, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    grade = (
        db.query(GradeRecord)
        .filter(
            GradeRecord.student_id == payload.student_id,
            GradeRecord.discipline_id == payload.discipline_id,
            GradeRecord.graded_at == payload.graded_at,
        )
        .first()
    )

    old_value = None
    if grade:
        old_value = str(grade.value)
        grade.value = payload.value
        grade.grade_type_id = payload.grade_type_id
        grade.comment = payload.comment
        grade.updated_by = user.id
    else:
        grade = GradeRecord(**payload.model_dump(), updated_by=user.id)
        db.add(grade)

    db.flush()
    write_audit_log(
        db,
        entity_name="grade_records",
        entity_id=grade.id,
        field_name="value",
        old_value=old_value,
        new_value=str(payload.value),
        changed_by=user.id,
    )
    db.commit()
    db.refresh(grade)
    return grade
