from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api.endpoints import router as api_router
from app.db.database import Base, engine
import app.models  # Ensures models are imported

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Dropping for phase 1 schema change
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="PocketForge API", version="0.1.0", lifespan=lifespan)

# Mount static directory for audio files
STATIC_DIR = os.path.join(os.getcwd(), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
