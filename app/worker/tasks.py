import time
import asyncio
from sqlalchemy.future import select
from app.worker.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.models.job import Job
from app.agents.graph import app as graph_app
from app.agents.state import AgentState
from app.services.audio import generate_line_audio, merge_audio

async def async_process_chapter(job_id: int):
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Job).filter(Job.id == job_id))
            job = result.scalars().first()
            if job:
                job.status = "Processing Text"
                await db.commit()
                
                # Setup Agent State
                initial_state = AgentState(
                    chapter_text=job.chapter_text,
                    director_breakdown=None,
                    script=None,
                    feedback=None,
                    revision_count=0
                )
                
                # Run LangGraph pipeline in a thread to avoid blocking the event loop
                final_state = await asyncio.to_thread(graph_app.invoke, initial_state)
                
                if final_state.get("script"):
                    # Update database with script and move to next stage
                    script_data = final_state["script"].model_dump()
                    job.script_json = script_data
                    job.status = "processing_audio"
                    await db.commit()
                    
                    # Generate audio for each line concurrently
                    lines = script_data.get("lines", [])
                    audio_tasks = [
                        generate_line_audio(job_id, i, line.get("speaker"), line.get("text"))
                        for i, line in enumerate(lines)
                    ]
                    
                    chunk_paths = await asyncio.gather(*audio_tasks)
                    
                    # Merge all audio chunks
                    final_url = merge_audio(job_id, chunk_paths)
                    
                    # Update job as completed
                    job.result_audio_url = final_url
                    job.status = "Completed"
                    await db.commit()
                    
                else:
                    job.status = "Failed"
                    job.script_json = {"error": "Failed to generate script"}
                    await db.commit()
                    
                return {"status": job.status, "job_id": job_id}
            return {"status": "Failed", "error": "Job not found"}
        except Exception as e:
            await db.rollback()
            import traceback
            traceback.print_exc()
            return {"status": "Failed", "error": str(e)}

@celery_app.task(bind=True)
def process_chapter_task(self, job_id: int):
    from app.db.database import engine
    async def run_task():
        try:
            return await async_process_chapter(job_id)
        finally:
            await engine.dispose()
    return asyncio.run(run_task())
