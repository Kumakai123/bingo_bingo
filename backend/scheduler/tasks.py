from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def setup_scheduler(db_session_factory) -> BackgroundScheduler:
    """
    Create and start the background scheduler.

    - Crawl every CRAWLER_INTERVAL_MINUTES (default 6 min)
    - After crawl, run analysis and update last_updated timestamp
    - max_instances=1 prevents concurrent crawl jobs
    """
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")

    def crawl_and_analyze_job():
        logger.info("排程爬蟲啟動...")
        db = db_session_factory()
        try:
            from crawler.bingo_crawler import BingoCrawler
            from app.api.status import set_last_updated

            crawler = BingoCrawler(db)
            stats = crawler.run()
            logger.info(f"排程爬蟲完成: {stats}")

            if stats["inserted"] > 0:
                set_last_updated()
                logger.info("已更新 last_updated 時間戳")

        except Exception as e:
            logger.error(f"排程爬蟲例外: {e}")
        finally:
            db.close()

    scheduler.add_job(
        crawl_and_analyze_job,
        trigger=IntervalTrigger(minutes=settings.CRAWLER_INTERVAL_MINUTES),
        id="bingo_crawler",
        name="BINGO 開獎資料爬蟲",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info(
        f"排程器已啟動 (每 {settings.CRAWLER_INTERVAL_MINUTES} 分鐘)"
    )
    return scheduler
