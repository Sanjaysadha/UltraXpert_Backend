from fastapi import APIRouter

from api.v1.endpoints import auth, patients, appointments, reports, scans, notifications, export_report, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(export_report.router, prefix="/export", tags=["export"])
