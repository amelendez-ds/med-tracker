import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from med_tracker.config import get_settings
from med_tracker.database import get_engine

TEST_CRON_SECRET = "test-secret"


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Point the app at a throwaway SQLite file and neutralise all real creds
    # BEFORE it builds its engine or reads settings. Each test is isolated.
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["CRON_SECRET"] = TEST_CRON_SECRET
    os.environ["DISCORD_WEBHOOK"] = ""  # blanked so no real alert can fire
    os.environ["RESEND_API_KEY"] = ""
    os.environ["EMAIL_ADDRESS"] = ""

    # Clear caches AFTER setting env, so the next call rebuilds from these values.
    get_settings.cache_clear()
    get_engine.cache_clear()

    from med_tracker.main import app

    with TestClient(app) as c:  # "with" runs the lifespan, which creates tables
        yield c

    get_settings.cache_clear()
    get_engine.cache_clear()
    os.close(db_fd)
    os.remove(db_path)
