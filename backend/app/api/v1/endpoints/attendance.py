from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import AttendanceRecord, Group, Student, User
from app.schemas.attendance import (
    AttendanceBulkPresent,
    AttendanceJournalResponse,
    AttendanceJournalSaveRequest,
    AttendanceUpsert,
    JournalSelectionQuery,
    StudentAttendanceRow,
)
from app.services.audit import write_audit_log

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/")
def list_attendance(discipline_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(AttendanceRecord).filter(AttendanceRecord.discipline_id == discipline_id).all()


@router.get("/journal", response_model=AttendanceJournalResponse)
def get_attendance_journal(
    academic_year_id: int = Query(...),
    semester_id: int = Query(...),
    study_form: str = Query(...),
    course_id: int = Query(...),
    group_id: int = Query(...),
    discipline_id: int = Query(...),
    lesson_date: date = Query(...),
    lesson_type_id: int = Query(1),
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
        return AttendanceJournalResponse(
            filters=JournalSelectionQuery(
                academic_year_id=academic_year_id,
                semester_id=semester_id,
                study_form=study_form,
                course_id=course_id,
                group_id=group_id,
                discipline_id=discipline_id,
                lesson_date=lesson_date,
                lesson_type_id=lesson_type_id,
            ),
            students=[],
        )

    students = db.query(Student).filter(Student.group_id == group.id).order_by(Student.full_name.asc()).all()

    existing = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.discipline_id == discipline_id,
            AttendanceRecord.lesson_date == lesson_date,
            AttendanceRecord.lesson_type_id == lesson_type_id,
            AttendanceRecord.student_id.in_([s.id for s in students]) if students else False,
        )
        .all()
    )
    existing_map = {record.student_id: record for record in existing}

    rows = [
        StudentAttendanceRow(
            student_id=student.id,
            full_name=student.full_name,
            attendance_record_id=existing_map.get(student.id).id if existing_map.get(student.id) else None,
            status_id=existing_map.get(student.id).status_id if existing_map.get(student.id) else None,
        )
        for student in students
    ]

    return AttendanceJournalResponse(
        filters=JournalSelectionQuery(
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            study_form=study_form,
            course_id=course_id,
            group_id=group_id,
            discipline_id=discipline_id,
            lesson_date=lesson_date,
            lesson_type_id=lesson_type_id,
        ),
        students=rows,
    )


@router.post("/journal/save")
def save_attendance_journal(
    payload: AttendanceJournalSaveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    updated = 0
    for item in payload.items:
        row = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.student_id == item.student_id,
                AttendanceRecord.discipline_id == payload.discipline_id,
                AttendanceRecord.lesson_date == payload.lesson_date,
                AttendanceRecord.lesson_type_id == payload.lesson_type_id,
            )
            .first()
        )

        old_value = None
        if row:
            old_value = str(row.status_id)
            row.status_id = item.status_id
            row.updated_by = user.id
        else:
            row = AttendanceRecord(
                student_id=item.student_id,
                discipline_id=payload.discipline_id,
                lesson_date=payload.lesson_date,
                lesson_type_id=payload.lesson_type_id,
                status_id=item.status_id,
                updated_by=user.id,
            )
            db.add(row)

        db.flush()
        write_audit_log(
            db,
            entity_name="attendance_records",
            entity_id=row.id,
            field_name="status_id",
            old_value=old_value,
            new_value=str(item.status_id),
            changed_by=user.id,
        )
        updated += 1

    db.commit()
    return {"updated": updated}


@router.post("/")
def upsert_attendance(payload: AttendanceUpsert, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.student_id == payload.student_id,
            AttendanceRecord.discipline_id == payload.discipline_id,
            AttendanceRecord.lesson_date == payload.lesson_date,
            AttendanceRecord.lesson_type_id == payload.lesson_type_id,
        )
        .first()
    )

    old_value = None
    if row:
        old_value = str(row.status_id)
        row.status_id = payload.status_id
        row.comment = payload.comment
        row.updated_by = user.id
    else:
        row = AttendanceRecord(**payload.model_dump(), updated_by=user.id)
        db.add(row)

    db.flush()
    write_audit_log(
        db,
        entity_name="attendance_records",
        entity_id=row.id,
        field_name="status_id",
        old_value=old_value,
        new_value=str(payload.status_id),
        changed_by=user.id,
    )
    db.commit()
    db.refresh(row)
    return row


@router.post("/bulk-all-present")
def bulk_all_present(payload: AttendanceBulkPresent, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    for student_id in payload.student_ids:
        row = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.discipline_id == payload.discipline_id,
                AttendanceRecord.lesson_date == payload.lesson_date,
                AttendanceRecord.lesson_type_id == payload.lesson_type_id,
            )
            .first()
        )
        if row:
            row.status_id = payload.present_status_id
            row.updated_by = user.id
        else:
            db.add(
                AttendanceRecord(
                    student_id=student_id,
                    discipline_id=payload.discipline_id,
                    lesson_date=payload.lesson_date,
                    lesson_type_id=payload.lesson_type_id,
                    status_id=payload.present_status_id,
                    updated_by=user.id,
                )
            )
    db.commit()
    return {"updated": len(payload.student_ids)}
