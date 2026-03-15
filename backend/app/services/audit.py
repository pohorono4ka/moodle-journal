from sqlalchemy.orm import Session

from app.models.models import AuditLog


def write_audit_log(db: Session, *, entity_name: str, entity_id: int, field_name: str, old_value: str | None, new_value: str | None, changed_by: int) -> None:
    db.add(
        AuditLog(
            entity_name=entity_name,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
        )
    )
