from fastapi import APIRouter

from app.api.v1.endpoints import attendance, audit, auth, grades, moodle_sync, reference_data, reports, roles, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(reference_data.router)
api_router.include_router(attendance.router)
api_router.include_router(grades.router)
api_router.include_router(moodle_sync.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)
