"""Run tests against a temporary database on this project's PostgreSQL server."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from todo_tracker.core.config import settings

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q"],
    cwd=root,
    env=dict(os.environ, TODO_TRACKER_TEST_DATABASE_URL=str(settings.DATABASE_URL)),
)
raise SystemExit(result.returncode)
