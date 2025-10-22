from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import  init_db
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run at startup
    init_db()
    host = "127.0.0.1"
    port = 8000
    print(f"API running at http://{host}:{port}")
    yield
    # Code to run at shutdown (optional)
    print("API shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

