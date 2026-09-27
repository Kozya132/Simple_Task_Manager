FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv/todo-tracker
COPY requirements.txt ./
RUN pip install -r requirements.txt && useradd --create-home --uid 10001 todo_tracker
COPY alembic.ini ./
COPY migrations ./migrations
COPY todo_tracker ./todo_tracker
USER todo_tracker
EXPOSE 8000
CMD ["uvicorn", "todo_tracker.main:app", "--host", "0.0.0.0", "--port", "8000"]
