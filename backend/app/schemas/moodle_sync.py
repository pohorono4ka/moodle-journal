from datetime import datetime

from pydantic import BaseModel


class SyncEntityStat(BaseModel):
    entity_name: str
    processed_count: int
    created_count: int
    updated_count: int
    error_count: int
    errors: str | None = None


class SyncRunResponse(BaseModel):
    run_id: int
    mode: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    summary: str | None
    entities: list[SyncEntityStat]


class SyncLatestResponse(BaseModel):
    last_sync_at: datetime | None
    last_status: str | None
    last_run_id: int | None


class SyncConfigResponse(BaseModel):
    mode: str
    base_url: str
