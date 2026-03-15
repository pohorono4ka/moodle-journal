from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.models import (
    AcademicYear,
    AttendanceStatus,
    AttendanceStatusCode,
    Course,
    Discipline,
    GradeRecord,
    GradeType,
    Group,
    LessonType,
    Role,
    Semester,
    Student,
    StudyForm,
    TeacherDisciplineGroup,
    User,
    UserRole,
    UserRoleLink,
)


def get_or_create(db: Session, model, defaults: dict | None = None, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    db.add(instance)
    db.flush()
    return instance


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        teacher_role = get_or_create(db, Role, code=UserRole.teacher, defaults={"name": "Преподаватель"})

        teacher = db.query(User).filter(User.email == "teacher@example.com").first()
        if not teacher:
            teacher = User(
                moodle_id=9001,
                email="teacher@example.com",
                full_name="Тестовый Преподаватель",
                password_hash=get_password_hash("Teacher123!"),
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.add(teacher)
            db.flush()

        if not teacher.moodle_id:
            teacher.moodle_id = 9001

        get_or_create(db, UserRoleLink, user_id=teacher.id, role_id=teacher_role.id)

        year = get_or_create(db, AcademicYear, name="2024/2025", defaults={"is_active": True})
        semester = get_or_create(db, Semester, name="1 семестр")
        course = get_or_create(db, Course, moodle_id=2001, defaults={"number": 2})
        group = get_or_create(
            db,
            Group,
            moodle_id=3001,
            code="ИС-21",
            defaults={"study_form": StudyForm.full_time, "course_id": course.id},
        )
        discipline = get_or_create(db, Discipline, moodle_id=4001, defaults={"name": "Базы данных"})

        lesson_type = get_or_create(db, LessonType, name="Лекция")

        get_or_create(db, AttendanceStatus, code=AttendanceStatusCode.present, defaults={"name": "Присутствовал"})
        get_or_create(db, AttendanceStatus, code=AttendanceStatusCode.absent, defaults={"name": "Отсутствовал"})
        get_or_create(db, AttendanceStatus, code=AttendanceStatusCode.excused, defaults={"name": "Уважительная причина"})
        get_or_create(db, AttendanceStatus, code=AttendanceStatusCode.late, defaults={"name": "Опоздал"})

        oral = get_or_create(db, GradeType, name="Устный ответ")
        self_work = get_or_create(db, GradeType, name="Самостоятельная работа")
        test_work = get_or_create(db, GradeType, name="Контрольная работа")
        boundary = get_or_create(db, GradeType, name="Рубежный контроль")

        get_or_create(
            db,
            TeacherDisciplineGroup,
            teacher_id=teacher.id,
            discipline_id=discipline.id,
            group_id=group.id,
        )

        students = [
            "Алиев Тимур Рустамович",
            "Ким Алина Сергеевна",
            "Петров Илья Андреевич",
            "Смирнова Дарья Павловна",
            "Абдуллаев Жасур Улугбекович",
            "Соколова Мария Викторовна",
            "Иванов Никита Олегович",
            "Ермекова Аружан Бауыржановна",
            "Кузнецов Артём Игоревич",
            "Морозова Екатерина Дмитриевна",
        ]

        created_students = []
        for idx, full_name in enumerate(students, start=1):
            student = get_or_create(
                db,
                Student,
                moodle_id=1000 + idx,
                defaults={
                    "full_name": full_name,
                    "email": f"student{idx}@example.com",
                    "group_id": group.id,
                },
            )
            created_students.append(student)

        demo_date = date.today()
        seed_grades = [
            (created_students[0], oral.id, 85),
            (created_students[1], self_work.id, 78),
            (created_students[2], test_work.id, 92),
            (created_students[3], boundary.id, 88),
        ]
        for student, grade_type_id, value in seed_grades:
            grade = (
                db.query(GradeRecord)
                .filter(
                    GradeRecord.student_id == student.id,
                    GradeRecord.discipline_id == discipline.id,
                    GradeRecord.graded_at == demo_date,
                )
                .first()
            )
            if grade:
                grade.value = value
                grade.grade_type_id = grade_type_id
                grade.updated_by = teacher.id
            else:
                db.add(
                    GradeRecord(
                        student_id=student.id,
                        discipline_id=discipline.id,
                        grade_type_id=grade_type_id,
                        value=value,
                        graded_at=demo_date,
                        updated_by=teacher.id,
                    )
                )

        db.commit()
        print("Seed completed successfully")
        print("Teacher login: teacher@example.com / Teacher123!")
        print(
            f"Academic year: {year.name}, semester: {semester.name}, group: {group.code}, discipline: {discipline.name}, lesson type: {lesson_type.name}"
        )
        print("Grade types: Устный ответ, Самостоятельная работа, Контрольная работа, Рубежный контроль")
        print(f"Demo grade date: {demo_date.isoformat()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
