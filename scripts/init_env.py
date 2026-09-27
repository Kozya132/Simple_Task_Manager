"""Generate project-local development credentials without replacing an existing .env."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
env_path = root / ".env"
password = secrets.token_hex(24)
content = (root / ".env.example").read_text().replace(
    "replace_with_random_password", password
).replace("replace_with_random_secret", secrets.token_hex(32))
try:
    with env_path.open("x") as env_file:
        env_path.chmod(0o600)
        env_file.write(content)
except FileExistsError:
    print("Existing .env preserved.")
else:
    print("Created .env with unique Todo-Tracker development credentials.")
