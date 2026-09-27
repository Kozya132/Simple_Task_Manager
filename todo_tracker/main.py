from contextlib import asynccontextmanager

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    yield

    print("Shutting down...")
    

app = FastAPI(
    title="Todo-Tracker API",
    lifespan=lifespan,)


@app.get("/")
async def root():
    return {"message": "Welcome to the Todo-Tracker API!"}
