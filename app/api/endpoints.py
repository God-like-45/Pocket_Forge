from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional, Any
from app.db.database import get_db
from app.models.job import Job
from app.worker.celery_app import celery_app

router = APIRouter()

class ChapterCreate(BaseModel):
    chapter_text: str

class JobResponse(BaseModel):
    id: int
    status: str
    chapter_text: str
    script_json: Optional[Any] = None
    result_audio_url: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/upload-chapter", response_model=JobResponse)
async def create_chapter(chapter: ChapterCreate, db: AsyncSession = Depends(get_db)):
    new_job = Job(chapter_text=chapter.chapter_text, status="Pending")
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Dispatch Celery task by name to avoid importing heavy ML libraries in the web process
    celery_app.send_task("app.worker.tasks.process_chapter_task", args=[new_job.id])

    return new_job

@router.get("/status/{job_id}", response_model=JobResponse)
async def get_chapter_status(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).filter(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
