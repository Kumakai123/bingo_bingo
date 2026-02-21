from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

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


@router.post("/refresh")
def refresh_now(db: Session = Depends(get_db)):
    """
    Manually trigger crawler immediately, then update timestamp.
    Frontend manual-refresh button can call this endpoint.
    """
    from crawler.bingo_crawler import BingoCrawler

    stats = BingoCrawler(db).run()
    set_last_updated()
    return {"ok": True, "stats": stats, "last_updated": _last_updated}
