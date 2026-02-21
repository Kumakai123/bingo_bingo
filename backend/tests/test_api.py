import os
import pytest
from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.draw_result import DrawResult
from app.api.status import set_last_updated
from app.api import status as status_mod


# ─── File-based test DB (thread-safe for TestClient) ──────────

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


def _seed(n=3):
    db = TestSession()
    for i in range(n):
        db.add(DrawResult(
            draw_term=f"11500{i:04d}",
            draw_date=date(2026, 1, 9),
            draw_datetime=datetime(2026, 1, 9, 14, 30 - i),
            numbers_sorted="01,02,03,04,05,41,42,43,44,45,06,07,08,09,10,46,47,48,49,50",
            numbers_sequence="01,02,03,04,05,41,42,43,44,45,06,07,08,09,10,46,47,48,49,50",
            super_number="44",
            high_low_result="大",
            high_count=10, low_count=10,
            odd_even_result="單",
            odd_count=10, even_count=10,
        ))
    db.commit()
    db.close()


# ─── Root / Health ────────────────────────────────────────────


class TestRootEndpoints:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["message"] == "BINGO 分析 API"

    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ─── Draws ────────────────────────────────────────────────────


class TestDrawsAPI:
    def test_latest_empty(self):
        r = client.get("/api/draws/latest")
        assert r.status_code == 200
        assert r.json() == []

    def test_latest_with_data(self):
        _seed(3)
        r = client.get("/api/draws/latest?limit=2")
        data = r.json()
        assert len(data) == 2
        assert "draw_term" in data[0]
        assert "numbers_sorted" in data[0]
        assert isinstance(data[0]["numbers_sorted"], list)

    def test_get_by_term(self):
        _seed(1)
        r = client.get("/api/draws/115000000")
        assert r.status_code == 200
        assert r.json()["draw_term"] == "115000000"

    def test_get_by_term_not_found(self):
        r = client.get("/api/draws/999999999")
        assert r.status_code == 404


# ─── Predictions ──────────────────────────────────────────────


class TestPredictionsAPI:
    def test_all_empty(self):
        r = client.get("/api/predictions/all?period_range=10")
        assert r.status_code == 200
        data = r.json()
        assert "basic" in data
        assert "super_number" in data
        assert "high_low" in data
        assert "odd_even" in data

    def test_all_with_data(self):
        _seed(15)
        r = client.get("/api/predictions/all?period_range=10")
        data = r.json()
        assert data["basic"]["period_range"] == 10
        assert len(data["basic"]["predictions"]) > 0

    def test_basic(self):
        _seed(10)
        r = client.get("/api/predictions/basic?period_range=10&top_n=5")
        assert r.status_code == 200
        data = r.json()
        assert data["prediction_type"] == "basic"
        assert len(data["predictions"]) == 5

    def test_super_number(self):
        _seed(10)
        r = client.get("/api/predictions/super-number?period_range=10")
        assert r.status_code == 200
        data = r.json()
        assert data["prediction_type"] == "super_number"

    def test_high_low(self):
        _seed(10)
        r = client.get("/api/predictions/high-low?period_range=10")
        assert r.status_code == 200
        assert "prediction" in r.json()

    def test_odd_even(self):
        _seed(10)
        r = client.get("/api/predictions/odd-even?period_range=10")
        assert r.status_code == 200
        assert "prediction" in r.json()


# ─── Status ───────────────────────────────────────────────────


class TestStatusAPI:
    def test_last_updated_initially_none(self):
        status_mod._last_updated = None
        r = client.get("/api/status/last-updated")
        assert r.status_code == 200
        assert r.json()["last_updated"] is None

    def test_last_updated_after_set(self):
        dt = datetime(2026, 2, 18, 14, 36, 0)
        set_last_updated(dt)
        r = client.get("/api/status/last-updated")
        assert r.status_code == 200
        assert r.json()["last_updated"] is not None
