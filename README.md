# Todo-Tracker

Standalone Python 3.12 / FastAPI application with async SQLAlchemy, PostgreSQL 16,
and Alembic. The Python import package is `todo_tracker`; the project folder is
`Todo-Tracker`.

## Run with Docker

```bash
cd /home/egor/Projects/Todo-Tracker
python3 scripts/init_env.py
docker compose up -d --build --wait
```

`init_env.py` creates `.env` with random local credentials and preserves an
existing file. PostgreSQL becomes healthy, the `migrate` service applies all
migrations, and then the API starts.

- API: http://127.0.0.1:8001/
- Swagger UI: http://127.0.0.1:8001/docs
- PostgreSQL: `127.0.0.1:5433`, database and user `todo_tracker`
- Compose project: `todo-tracker`
- Database volume: `todo-tracker_postgres_data`
- Network: `todo-tracker_default`
- API image: `todo-tracker-api:local`

```bash
docker compose ps -a
docker compose logs migrate api
docker compose stop
```

`docker compose down` also preserves database data. Adding `--volumes` deletes
this project's database. The old `todo_postgres` container and
`app_postgres_data` volume are preserved separately; their data is not imported
into this fresh database.

## Local development

Use a separate virtual environment in this folder, not a parent folder's or
Iron Track's environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/init_env.py
docker compose up -d --wait postgres
python -m alembic upgrade head
python -m uvicorn todo_tracker.main:app --reload --port 8001
```

If the Docker API already uses port 8001, stop it with `docker compose stop api`
before running the local API. No system PostgreSQL changes are needed.

Configuration is read from this project's `.env`, regardless of the current
working directory. Only `TODO_TRACKER_*` variables configure the application;
generic `DATABASE_URL` and `JWT_SECRET` variables from another project are ignored.
Compose uses its internal database hostname; local Python uses `127.0.0.1:5433`.
If you change the database port, update both `TODO_TRACKER_POSTGRES_PORT` and
`TODO_TRACKER_DATABASE_URL` in `.env`. Keep generated credentials out of Git.

## Migrations

The initial revision is `0001`, creating `users`, `tasks`, task status/priority
enums, unique username/email constraints, and the task owner foreign key/index.
After editing models, import any new model modules in `todo_tracker/models/__init__.py`,
then run:

```bash
source .venv/bin/activate
python -m alembic revision --autogenerate -m "describe schema change"
# Review the generated upgrade and downgrade before applying it.
python -m alembic upgrade head
python -m alembic check
python -m alembic current
```

For an application running entirely in Docker:

```bash
docker compose run --rm migrate alembic current
docker compose run --rm migrate alembic upgrade head
```

Use the local environment to generate revisions so the new files stay on the
host. Rebuild the image after changing migration or application files.

## Verification

```bash
python -m pip check
python -m pytest -q
```

The migration integration test is opt-in. Run it against the isolated local
Todo-Tracker database server using the credentials already loaded from `.env`:

```bash
python scripts/verify.py
```

It creates a uniquely named temporary database, checks upgrade, metadata drift,
constraints, downgrade (including enum removal), and re-upgrade, then drops only
that temporary database. The configured database user's role must be allowed to
create databases; the local Compose user can do this.

`requirements.txt` pins direct and transitive dependencies. To intentionally
refresh it with uv, run `uv pip compile requirements.in --python .venv/bin/python
--output-file requirements.txt` and repeat verification.

The API currently contains the welcome endpoint. Auth and task routes are still
scaffolding; this setup prepares the database and runtime for their implementation.

Reference: [Alembic async migrations](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic),
[Compose startup ordering](https://docs.docker.com/compose/how-tos/startup-order/).
