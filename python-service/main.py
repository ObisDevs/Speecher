import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from tts_engine import TTSEngine
from job_processor import JobProcessor
from supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Speecher AI Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
tts_engine = TTSEngine()
job_processor = JobProcessor()
supabase_client = SupabaseClient()

class JobRequest(BaseModel):
    job_id: str
    job_type: str
    input_data: Dict[str, Any]
    user_id: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "tts_engine": "ready",
            "job_processor": "ready",
            "supabase": "connected"
        }
    )

@app.post("/process-job")
async def process_job(job_request: JobRequest, background_tasks: BackgroundTasks):
    """Process a TTS job"""
    try:
        logger.info(f"Processing job {job_request.job_id} of type {job_request.job_type}")
        
        # Add job to background processing
        background_tasks.add_task(
            job_processor.process_job,
            job_request.job_id,
            job_request.job_type,
            job_request.input_data,
            job_request.user_id
        )
        
        return {"status": "accepted", "job_id": job_request.job_id}
        
    except Exception as e:
        logger.error(f"Error processing job {job_request.job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}/status")
async def get_job_status(job_id: str):
    """Get job status"""
    try:
        status = await supabase_client.get_job_status(job_id)
        return status
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Speecher AI Service...")
    await tts_engine.initialize()
    await supabase_client.initialize()
    logger.info("All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Speecher AI Service...")
    await tts_engine.cleanup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)