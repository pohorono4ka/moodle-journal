from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(User).all()
