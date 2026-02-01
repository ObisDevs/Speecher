import os
import logging
from typing import Dict, Any, Optional
from supabase import create_client, Client
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Optional[Client] = None
        self.url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
    async def initialize(self):
        """Initialize Supabase client"""
        try:
            if not self.url or not self.service_key:
                raise ValueError("Missing Supabase credentials")
            
            self.client = create_client(self.url, self.service_key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status from database"""
        try:
            response = self.client.table("jobs").select("*").eq("id", job_id).single().execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to get job status {job_id}: {str(e)}")
            raise
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        progress: int = None,
        progress_message: str = None,
        result_data: Dict[str, Any] = None,
        error_code: str = None,
        error_message: str = None
    ):
        """Update job status in database"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if progress is not None:
                update_data["progress"] = progress
            
            if progress_message:
                update_data["progress_message"] = progress_message
            
            if result_data:
                update_data["result_data"] = result_data
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            if error_code:
                update_data["error_code"] = error_code
            
            if error_message:
                update_data["error_message"] = error_message
            
            if status == "processing" and "started_at" not in update_data:
                update_data["started_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("jobs").update(update_data).eq("id", job_id).execute()
            
            logger.info(f"Updated job {job_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update job status {job_id}: {str(e)}")
            raise
    
    async def upload_audio(self, audio_data: bytes, file_path: str) -> str:
        """Upload audio file to Supabase storage"""
        try:
            # Upload to audio-outputs bucket
            response = self.client.storage.from_("audio-outputs").upload(
                file_path, 
                audio_data,
                file_options={"content-type": "audio/wav"}
            )
            
            if response.error:
                raise Exception(f"Upload failed: {response.error}")
            
            # Get public URL
            public_url = self.client.storage.from_("audio-outputs").get_public_url(file_path)
            
            logger.info(f"Audio uploaded successfully: {file_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload audio {file_path}: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to get user profile {user_id}: {str(e)}")
            raise
    
    async def update_user_usage(self, user_id: str, minutes_used: float):
        """Update user's monthly usage"""
        try:
            # Get current usage
            profile = await self.get_user_profile(user_id)
            current_usage = profile.get("usage_this_month", 0)
            
            # Update usage
            new_usage = current_usage + minutes_used
            
            response = self.client.table("profiles").update({
                "usage_this_month": new_usage,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            logger.info(f"Updated user {user_id} usage: +{minutes_used} minutes")
            
        except Exception as e:
            logger.error(f"Failed to update user usage {user_id}: {str(e)}")
            raise