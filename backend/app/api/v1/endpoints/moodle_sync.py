import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.models import MoodleSyncLog, MoodleSyncRun, User
from app.schemas.moodle_sync import SyncConfigResponse, SyncEntityStat, SyncLatestResponse, SyncRunResponse
from app.services.moodle_sync import run_moodle_sync

router = APIRouter(prefix="/moodle-sync", tags=["moodle_sync"])


def _run_to_response(db: Session, run: MoodleSyncRun) -> SyncRunResponse:
    logs = db.query(MoodleSyncLog).filter(MoodleSyncLog.run_id == run.id).all()
    entities = [
        SyncEntityStat(
            entity_name=log.entity_name,
            processed_count=log.processed_count,
            created_count=log.created_count,
            updated_count=log.updated_count,
            error_count=log.error_count,
            errors=log.errors,
        )
        for log in logs
    ]

    summary = run.summary
    if summary:
        try:
            parsed_summary = json.loads(summary)
            summary = json.dumps(parsed_summary, ensure_ascii=False)
        except json.JSONDecodeError:
            pass

    return SyncRunResponse(
        run_id=run.id,
        mode=run.mode,
        status=run.status.value,
        started_at=run.started_at,
        finished_at=run.finished_at,
        summary=summary,
        entities=entities,
    )


@router.get("/config", response_model=SyncConfigResponse)
def get_sync_config(_=Depends(get_current_user)):
    return SyncConfigResponse(mode=settings.moodle_sync_mode.lower(), base_url=settings.moodle_base_url)


@router.post("/run", response_model=SyncRunResponse)
def run_sync(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run = run_moodle_sync(db, triggered_by=user.id)
    return _run_to_response(db, run)


@router.get("/runs/latest", response_model=SyncLatestResponse)
def latest_sync(db: Session = Depends(get_db), _=Depends(get_current_user)):
    run = db.query(MoodleSyncRun).order_by(MoodleSyncRun.started_at.desc()).first()
    if not run:
        return SyncLatestResponse(last_sync_at=None, last_status=None, last_run_id=None)
    return SyncLatestResponse(last_sync_at=run.started_at, last_status=run.status.value, last_run_id=run.id)


@router.get("/runs/{run_id}", response_model=SyncRunResponse)
def sync_run_detail(run_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    run = db.query(MoodleSyncRun).filter(MoodleSyncRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Sync run not found")
    return _run_to_response(db, run)


@router.get("/runs", response_model=list[SyncRunResponse])
def list_sync_runs(limit: int = 20, db: Session = Depends(get_db), _=Depends(get_current_user)):
    runs = db.query(MoodleSyncRun).order_by(MoodleSyncRun.started_at.desc()).limit(limit).all()
    return [_run_to_response(db, run) for run in runs]
