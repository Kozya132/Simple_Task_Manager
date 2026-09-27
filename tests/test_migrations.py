"""Opt-in PostgreSQL checks; every run creates and drops its own temporary database."""
import asyncio
import os
from pathlib import Path
import subprocess
import sys
import uuid

import asyncpg
import pytest
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]


def test_initial_migration_round_trip():
    admin_url = os.getenv("TODO_TRACKER_TEST_DATABASE_URL")
    if not admin_url:
        pytest.skip("Set TODO_TRACKER_TEST_DATABASE_URL to an isolated PostgreSQL server")
    url = make_url(admin_url)
    database = "todo_tracker_test_" + uuid.uuid4().hex
    test_url = url.set(database=database)

    async def admin(statement):
        connection = await asyncpg.connect(url.set(drivername="postgresql").render_as_string(hide_password=False))
        try:
            await connection.execute(statement)
        finally:
            await connection.close()

    def alembic(*args):
        env = dict(os.environ, TODO_TRACKER_DATABASE_URL=test_url.render_as_string(hide_password=False))
        subprocess.run(
            [sys.executable, "-m", "alembic", "-c", str(ROOT / "alembic.ini"), *args],
            cwd="/tmp", env=env, check=True, capture_output=True, text=True,
        )

    async def check_schema():
        connection = await asyncpg.connect(test_url.set(drivername="postgresql").render_as_string(hide_password=False))
        try:
            assert await connection.fetchval("SELECT version_num FROM alembic_version") == "0001"
            user_id = uuid.uuid4()
            await connection.execute(
                "INSERT INTO users (id, username, email, hashed_password, is_active) VALUES ($1, 'tester', 'test@example.com', 'hash', true)",
                user_id,
            )
            await connection.execute(
                "INSERT INTO tasks (id, user_id, title, status, priority) VALUES ($1, $2, 'First task', 'PENDING', 'MEDIUM')",
                uuid.uuid4(), user_id,
            )
            assert await connection.fetchval("SELECT count(*) FROM tasks") == 1
            with pytest.raises(asyncpg.ForeignKeyViolationError):
                await connection.execute(
                    "INSERT INTO tasks (id, user_id, title, status, priority) VALUES ($1, $2, 'Orphan', 'PENDING', 'LOW')",
                    uuid.uuid4(), uuid.uuid4(),
                )
            with pytest.raises(asyncpg.UniqueViolationError):
                await connection.execute(
                    "INSERT INTO users (id, username, email, hashed_password, is_active) VALUES ($1, 'tester', 'other@example.com', 'hash', true)",
                    uuid.uuid4(),
                )
        finally:
            await connection.close()

    async def check_downgrade():
        connection = await asyncpg.connect(test_url.set(drivername="postgresql").render_as_string(hide_password=False))
        try:
            assert await connection.fetchval("SELECT to_regclass('public.tasks')") is None
            assert await connection.fetchval("SELECT to_regclass('public.users')") is None
            assert await connection.fetchval("SELECT count(*) FROM pg_type WHERE typname IN ('taskstatus', 'taskpriority')") == 0
        finally:
            await connection.close()

    asyncio.run(admin(f'CREATE DATABASE "{database}"'))
    try:
        alembic("upgrade", "head")
        alembic("check")
        asyncio.run(check_schema())
        alembic("downgrade", "base")
        asyncio.run(check_downgrade())
        alembic("upgrade", "head")
        alembic("check")
    finally:
        asyncio.run(admin(f'DROP DATABASE "{database}" WITH (FORCE)'))
