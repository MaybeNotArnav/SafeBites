"""Admin-only analytics endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies.auth import require_admin_user
from app.services import analytics_service

router = APIRouter(prefix="/admin", tags=["admin"])


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {value}") from exc


@router.get("/analytics")
def get_admin_analytics(
    start_date: str | None = Query(None, description="ISO date e.g. 2024-11-01"),
    end_date: str | None = Query(None, description="ISO date e.g. 2024-11-30"),
    restaurant_id: str | None = Query(None, description="Filter by restaurant id"),
    current_user=Depends(require_admin_user),
):
    """Return aggregated metrics for admins."""
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    return analytics_service.get_platform_analytics(start_dt, end_dt, restaurant_id)
