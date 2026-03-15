from fastapi import APIRouter, Depends

from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/journal-gaps")
def journal_gaps(_=Depends(get_current_user)):
    return {"message": "MVP report endpoint for unfilled journals"}
