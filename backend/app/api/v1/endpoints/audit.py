from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/")
def list_audit_logs(limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(AuditLog).order_by(AuditLog.changed_at.desc()).limit(limit).all()
