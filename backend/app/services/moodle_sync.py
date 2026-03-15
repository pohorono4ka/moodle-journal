import json
import secrets
from dataclasses import dataclass
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import (
    Course,
    Discipline,
    Group,
    MoodleSyncLog,
    MoodleSyncRun,
    Role,
    Student,
    StudyForm,
    SyncStatus,
    TeacherDisciplineGroup,
    User,
    UserRole,
    UserRoleLink,
)


@dataclass
class EntityCounter:
    processed: int = 0
    created: int = 0
    updated: int = 0
    errors: list[str] | None = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class MoodleApiClient:
    def __init__(self, base_url: str, token: str, timeout_seconds: int = 30):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds

    def call(self, function_name: str, **params):
        if not self.token:
            raise ValueError("MOODLE_TOKEN is empty")

        endpoint = f"{self.base_url}/webservice/rest/server.php"
        request_params = {
            "wstoken": self.token,
            "wsfunction": function_name,
            "moodlewsrestformat": "json",
            **params,
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(endpoint, params=request_params)
            response.raise_for_status()
            data = response.json()

        if isinstance(data, dict) and data.get("exception"):
            raise RuntimeError(f"Moodle error [{data.get('errorcode')}]: {data.get('message')}")
        return data


def load_moodle_payload() -> dict:
    mode = settings.moodle_sync_mode.lower()
    if mode == "demo":
        return {
            "teachers": [
                {"id": 9001, "email": "teacher@example.com", "full_name": "Тестовый Преподаватель"},
                {"id": 9002, "email": "teacher2@example.com", "full_name": "Преподаватель из Moodle"},
            ],
            "courses": [
                {"id": 2001, "number": 2},
                {"id": 2002, "number": 3},
            ],
            "groups": [
                {"id": 3001, "code": "ИС-21", "study_form": "full_time", "course_moodle_id": 2001},
                {"id": 3002, "code": "ИС-31", "study_form": "full_time", "course_moodle_id": 2002},
            ],
            "disciplines": [
                {"id": 4001, "name": "Базы данных"},
                {"id": 4002, "name": "Алгоритмы и структуры данных"},
            ],
            "students": [
                {"id": 1001, "full_name": "Алиев Тимур Рустамович", "email": "student1@example.com", "group_moodle_id": 3001},
                {"id": 1002, "full_name": "Ким Алина Сергеевна", "email": "student2@example.com", "group_moodle_id": 3001},
                {"id": 1003, "full_name": "Петров Илья Андреевич", "email": "student3@example.com", "group_moodle_id": 3001},
                {"id": 1004, "full_name": "Смирнова Дарья Павловна", "email": "student4@example.com", "group_moodle_id": 3001},
            ],
            "teacher_discipline_group_links": [
                {"teacher_moodle_id": 9001, "discipline_moodle_id": 4001, "group_moodle_id": 3001},
                {"teacher_moodle_id": 9002, "discipline_moodle_id": 4002, "group_moodle_id": 3002},
            ],
        }

    client = MoodleApiClient(settings.moodle_base_url, settings.moodle_token, settings.moodle_timeout_seconds)
    return client.call("local_journal_export_structure")


def _ensure_teacher_role(db: Session) -> Role:
    role = db.query(Role).filter(Role.code == UserRole.teacher).first()
    if role:
        return role
    role = Role(code=UserRole.teacher, name="Преподаватель")
    db.add(role)
    db.flush()
    return role


def _save_entity_log(db: Session, run_id: int, entity: str, counter: EntityCounter):
    db.add(
        MoodleSyncLog(
            run_id=run_id,
            entity_name=entity,
            processed_count=counter.processed,
            created_count=counter.created,
            updated_count=counter.updated,
            error_count=len(counter.errors or []),
            errors="\n".join(counter.errors or []) if counter.errors else None,
        )
    )


def _upsert_teachers(db: Session, items: list[dict]) -> EntityCounter:
    counter = EntityCounter()
    teacher_role = _ensure_teacher_role(db)
    for item in items:
        counter.processed += 1
        try:
            teacher = db.query(User).filter(User.moodle_id == int(item["id"])).first()
            if teacher:
                teacher.full_name = item.get("full_name", teacher.full_name)
                teacher.email = item.get("email") or teacher.email
                counter.updated += 1
            else:
                email = item.get("email") or f"moodle_teacher_{item['id']}@example.com"
                teacher = db.query(User).filter(User.email == email).first()
                if teacher:
                    teacher.moodle_id = int(item["id"])
                    teacher.full_name = item.get("full_name", teacher.full_name)
                    counter.updated += 1
                else:
                    teacher = User(
                        moodle_id=int(item["id"]),
                        email=email,
                        full_name=item.get("full_name", f"Teacher {item['id']}"),
                        password_hash=get_password_hash(secrets.token_urlsafe(20)),
                        is_active=True,
                    )
                    db.add(teacher)
                    db.flush()
                    counter.created += 1

            role_link = db.query(UserRoleLink).filter(UserRoleLink.user_id == teacher.id, UserRoleLink.role_id == teacher_role.id).first()
            if not role_link:
                db.add(UserRoleLink(user_id=teacher.id, role_id=teacher_role.id))
        except Exception as exc:  # noqa: BLE001
            counter.errors.append(f"teacher:{item.get('id')} -> {exc}")
    return counter


def _upsert_courses(db: Session, items: list[dict]) -> EntityCounter:
    counter = EntityCounter()
    for item in items:
        counter.processed += 1
        try:
            moodle_id = int(item["id"])
            number = int(item.get("number") or 1)
            row = db.query(Course).filter(Course.moodle_id == moodle_id).first()
            if row:
                row.number = number
                counter.updated += 1
            else:
                db.add(Course(moodle_id=moodle_id, number=number))
                counter.created += 1
        except Exception as exc:  # noqa: BLE001
            counter.errors.append(f"course:{item.get('id')} -> {exc}")
    return counter


def _upsert_groups(db: Session, items: list[dict]) -> EntityCounter:
    counter = EntityCounter()
    for item in items:
        counter.processed += 1
        try:
            course = db.query(Course).filter(Course.moodle_id == int(item["course_moodle_id"])).first()
            if not course:
                raise ValueError("course not found")

            row = db.query(Group).filter(Group.moodle_id == int(item["id"])).first()
            study_form = StudyForm(item.get("study_form", "full_time"))
            if row:
                row.code = item.get("code", row.code)
                row.study_form = study_form
                row.course_id = course.id
                counter.updated += 1
            else:
                db.add(
                    Group(
                        moodle_id=int(item["id"]),
                        code=item.get("code", f"GROUP-{item['id']}"),
                        study_form=study_form,
                        course_id=course.id,
                    )
                )
                counter.created += 1
        except Exception as exc:  # noqa: BLE001
            counter.errors.append(f"group:{item.get('id')} -> {exc}")
    return counter


def _upsert_disciplines(db: Session, items: list[dict]) -> EntityCounter:
    counter = EntityCounter()
    for item in items:
        counter.processed += 1
        try:
            row = db.query(Discipline).filter(Discipline.moodle_id == int(item["id"])).first()
            if row:
                row.name = item.get("name", row.name)
                counter.updated += 1
            else:
                db.add(Discipline(moodle_id=int(item["id"]), name=item.get("name", f"Discipline {item['id']}")))
                counter.created += 1
        except Exception as exc:  # noqa: BLE001
            counter.errors.append(f"discipline:{item.get('id')} -> {exc}")
    return counter


def _upsert_students(db: Session, items: list[dict]) -> EntityCounter:
    counter = EntityCounter()
    for item in items:
        counter.processed += 1
        try:
            group = db.query(Group).filter(Group.moodle_id == int(item["group_moodle_id"])).first()
            if not group:
                raise ValueError("group not found")

            row = db.query(Student).filter(Student.moodle_id == int(item["id"])).first()
            if row:
                row.full_name = item.get("full_name", row.full_name)
                row.email = item.get("email", row.email)
                row.group_id = group.id
                counter.updated += 1
            else:
                db.add(
                    Student(
                        moodle_id=int(item["id"]),
                        full_name=item.get("full_name", f"Student {item['id']}"),
                        email=item.get("email"),
                        group_id=group.id,
                    )
                )
                counter.created += 1
        except Exception as exc:  # noqa: BLE001
            counter.errors.append(f"student:{item.get('id')} -> {exc}")
    return counter


def _upsert_links(db: Session, items: list[dict]) -> EntityCounter:
    counter = EntityCounter()
    for item in items:
        counter.processed += 1
        try:
            teacher = db.query(User).filter(User.moodle_id == int(item["teacher_moodle_id"])).first()
            discipline = db.query(Discipline).filter(Discipline.moodle_id == int(item["discipline_moodle_id"])).first()
            group = db.query(Group).filter(Group.moodle_id == int(item["group_moodle_id"])).first()
            if not (teacher and discipline and group):
                raise ValueError("teacher/discipline/group not found")

            row = (
                db.query(TeacherDisciplineGroup)
                .filter(
                    TeacherDisciplineGroup.teacher_id == teacher.id,
                    TeacherDisciplineGroup.discipline_id == discipline.id,
                    TeacherDisciplineGroup.group_id == group.id,
                )
                .first()
            )
            if row:
                counter.updated += 1
            else:
                db.add(
                    TeacherDisciplineGroup(
                        teacher_id=teacher.id,
                        discipline_id=discipline.id,
                        group_id=group.id,
                    )
                )
                counter.created += 1
        except Exception as exc:  # noqa: BLE001
            counter.errors.append(f"link:{item} -> {exc}")
    return counter


def run_moodle_sync(db: Session, triggered_by: int | None = None) -> MoodleSyncRun:
    run = MoodleSyncRun(
        triggered_by=triggered_by,
        mode=settings.moodle_sync_mode.lower(),
        status=SyncStatus.success,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.flush()

    try:
        payload = load_moodle_payload()

        entity_counters = {
            "teachers": _upsert_teachers(db, payload.get("teachers", [])),
            "courses": _upsert_courses(db, payload.get("courses", [])),
            "groups": _upsert_groups(db, payload.get("groups", [])),
            "disciplines": _upsert_disciplines(db, payload.get("disciplines", [])),
            "students": _upsert_students(db, payload.get("students", [])),
            "teacher_discipline_group_links": _upsert_links(db, payload.get("teacher_discipline_group_links", [])),
        }

        has_errors = any(counter.errors for counter in entity_counters.values())
        run.status = SyncStatus.partial if has_errors else SyncStatus.success

        summary = {
            key: {
                "processed": value.processed,
                "created": value.created,
                "updated": value.updated,
                "errors": len(value.errors or []),
            }
            for key, value in entity_counters.items()
        }
        run.summary = json.dumps(summary, ensure_ascii=False)
        run.finished_at = datetime.utcnow()

        for entity_name, counter in entity_counters.items():
            _save_entity_log(db, run.id, entity_name, counter)

        db.commit()
        db.refresh(run)
        return run

    except Exception as exc:  # noqa: BLE001
        run.status = SyncStatus.failed
        run.finished_at = datetime.utcnow()
        run.summary = json.dumps({"error": str(exc)}, ensure_ascii=False)
        _save_entity_log(db, run.id, "sync_failed", EntityCounter(processed=0, created=0, updated=0, errors=[str(exc)]))
        db.commit()
        db.refresh(run)
        return run
