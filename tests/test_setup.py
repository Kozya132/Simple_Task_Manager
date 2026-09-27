from pathlib import Path

import httpx
import pytest

from todo_tracker.core.config import Settings
from todo_tracker.main import app


def test_settings_ignore_other_projects_and_work_from_any_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "postgresql://wrong:wrong@localhost/irontrack")
    monkeypatch.setenv("JWT_SECRET", "wrong-project")
    settings = Settings()
    assert settings.DATABASE_URL.path == "/todo_tracker"
    assert settings.JWT_SECRET != "wrong-project"
    assert Path(Settings.model_config["env_file"]).is_absolute()


@pytest.mark.asyncio
async def test_api_starts():
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Todo-Tracker API!"}
