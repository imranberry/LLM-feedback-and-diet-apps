import pytest

from diet_assistant import config


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test gets its own empty SQLite file."""
    db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db))
    monkeypatch.setattr(config, "DB_CONNECTION_STRING", f"sqlite:///{db}")
