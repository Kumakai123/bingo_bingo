from datetime import datetime

from fastapi import APIRouter

router = APIRouter()

# In-memory timestamp — updated by crawler after each successful run
_last_updated: datetime | None = None


def set_last_updated(dt: datetime | None = None):
    """Called by crawler/scheduler after successful crawl+analysis."""
    global _last_updated
    _last_updated = dt or datetime.now()


def get_last_updated() -> datetime | None:
    return _last_updated


@router.get("/last-updated")
def last_updated():
    return {"last_updated": _last_updated}
