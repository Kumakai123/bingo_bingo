import requests
import ssl
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from requests.adapters import HTTPAdapter

from app.config import settings
from app.models.draw_result import DrawResult
from app.models.crawler_log import CrawlerLog

logger = logging.getLogger(__name__)


class RelaxedStrictTLSAdapter(HTTPAdapter):
    """
    Keep certificate verification enabled, but disable strict X509 extension check.

    Some endpoints fail on newer OpenSSL builds due strict validation rules
    (e.g. missing Subject Key Identifier in cert chain).
    """

    def __init__(self, *args, **kwargs):
        self._ssl_context = ssl.create_default_context()
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            self._ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["ssl_context"] = self._ssl_context
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        proxy_kwargs["ssl_context"] = self._ssl_context
        return super().proxy_manager_for(proxy, **proxy_kwargs)


class BingoCrawler:
    """台灣彩券 BINGO BINGO 爬蟲"""

    API_BASE_URL = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/BingoResult"

    def __init__(self, db_session: Session):
        self.db = db_session
        self.session = requests.Session()
        if settings.CRAWLER_RELAX_TLS_STRICT:
            self.session.mount("https://", RelaxedStrictTLSAdapter())
            logger.warning(
                "CRAWLER_RELAX_TLS_STRICT=true: TLS strict validation is relaxed for crawler requests."
            )
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

    # ─── Main flow ────────────────────────────────────────

    def run(self) -> Dict[str, int]:
        stats = {"fetched": 0, "inserted": 0, "skipped": 0, "failed": 0}

        log_entry = CrawlerLog(started_at=datetime.now(), status="running")
        self.db.add(log_entry)
        self.db.commit()

        try:
            draw_list = self.fetch_latest_draws()
            stats["fetched"] = len(draw_list)

            for draw_data in draw_list:
                result = self.parse_and_save(draw_data)
                if result == "inserted":
                    stats["inserted"] += 1
                elif result == "skipped":
                    stats["skipped"] += 1
                else:
                    stats["failed"] += 1

            log_entry.status = "success"
            log_entry.finished_at = datetime.now()
            log_entry.records_fetched = stats["fetched"]
            log_entry.records_inserted = stats["inserted"]
            log_entry.records_skipped = stats["skipped"]
            self.db.commit()
            logger.info(f"爬蟲完成: {stats}")

        except Exception as e:
            log_entry.status = "failed"
            log_entry.error_message = str(e)
            log_entry.finished_at = datetime.now()
            self.db.commit()
            logger.error(f"爬蟲失敗: {e}")

        return stats

    # ─── Fetch ────────────────────────────────────────────

    def fetch_latest_draws(
        self,
        target_date: Optional[datetime] = None,
        page_size: int = 50,
    ) -> List[Dict]:
        if target_date is None:
            target_date = datetime.now()

        results = []
        dates_to_check = [
            target_date.date(),
            (target_date - timedelta(days=1)).date(),
        ]

        for check_date in dates_to_check:
            try:
                params = {
                    "openDate": check_date.strftime("%Y-%m-%d"),
                    "pageNum": 1,
                    "pageSize": page_size,
                }
                logger.info(f"查詢 {check_date} ...")
                resp = self.session.get(
                    self.API_BASE_URL, params=params, timeout=10
                )
                resp.raise_for_status()
                data = resp.json()

                if data.get("rtCode") == 0:
                    draws = data["content"]["bingoQueryResult"]
                    results.extend(draws)
                    logger.info(f"取得 {len(draws)} 筆")
                else:
                    logger.error(f"API 錯誤: {data.get('rtMsg')}")

            except requests.RequestException as e:
                logger.error(f"網路錯誤: {e}")
            except Exception as e:
                logger.error(f"未知錯誤: {e}")

        return results

    # ─── Validate ─────────────────────────────────────────

    def _validate(self, data: Dict) -> bool:
        required = ["drawTerm", "openShowOrder", "bigShowOrder", "bullEyeTop"]
        for field in required:
            if field not in data:
                logger.warning(f"缺少欄位: {field}")
                return False

        seq = data["openShowOrder"]

        if len(seq) != 20:
            logger.warning(f"號碼數量錯誤: {len(seq)}")
            return False

        if data["bullEyeTop"] != seq[-1]:
            logger.warning("bullEyeTop 與第 20 個號碼不符")
            return False

        try:
            nums = [int(n) for n in seq]
        except ValueError:
            logger.warning("號碼格式錯誤")
            return False

        if not all(1 <= n <= 80 for n in nums):
            logger.warning("號碼超出範圍 01-80")
            return False

        if len(set(nums)) != 20:
            logger.warning("號碼有重複")
            return False

        return True

    # ─── Parse ────────────────────────────────────────────

    def _parse_draw_data(self, data: Dict) -> Dict:
        draw_term = str(data["drawTerm"])
        numbers = [int(n) for n in data["openShowOrder"]]

        # Parse draw_date from drawTerm: 115009534
        # 115 = 民國年, 009 = day of year
        roc_year = int(draw_term[:3])
        day_of_year = int(draw_term[3:6])
        western_year = roc_year + 1911
        draw_date_val = date(western_year, 1, 1) + timedelta(days=day_of_year - 1)

        return {
            "draw_term": draw_term,
            "draw_date": draw_date_val,
            "draw_datetime": datetime.combine(draw_date_val, datetime.now().time()),
            "numbers_sorted": ",".join(data["bigShowOrder"]),
            "numbers_sequence": ",".join(data["openShowOrder"]),
            "super_number": data["bullEyeTop"],
            "high_low_result": data.get("highLowTop", "－"),
            "high_count": sum(1 for n in numbers if n >= 41),
            "low_count": sum(1 for n in numbers if n <= 40),
            "odd_even_result": data.get("oddEvenTop", "－"),
            "odd_count": sum(1 for n in numbers if n % 2 == 1),
            "even_count": sum(1 for n in numbers if n % 2 == 0),
        }

    # ─── Save ─────────────────────────────────────────────

    def parse_and_save(self, draw_data: Dict) -> str:
        if not self._validate(draw_data):
            return "failed"

        parsed = self._parse_draw_data(draw_data)

        try:
            existing = (
                self.db.query(DrawResult)
                .filter_by(draw_term=parsed["draw_term"])
                .first()
            )
            if existing:
                return "skipped"

            obj = DrawResult(**parsed)
            self.db.add(obj)
            self.db.commit()
            return "inserted"

        except IntegrityError:
            self.db.rollback()
            logger.warning(f"重複期號: {parsed['draw_term']}")
            return "skipped"
        except Exception as e:
            self.db.rollback()
            logger.error(f"儲存失敗: {e}")
            return "failed"
