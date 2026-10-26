import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

@pytest.fixture()
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path/'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine); Local = sessionmaker(bind=engine)
    def override():
        db=Local()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client: yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def session_id(): return "test-session-identifier-12345"
