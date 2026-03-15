from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Role

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/")
def list_roles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Role).all()
