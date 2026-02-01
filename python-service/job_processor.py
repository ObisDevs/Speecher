import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import uuid
import base64

from tts_engine import TTSEngine
from supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class JobProcessor:
    def __init__(self):
        self.tts_engine = TTSEngine()
        self.supabase_client = SupabaseClient()
        
    async def process_job(self, job_id: str, job_type: str, input_data: Dict[str, Any], user_id: str):
        """Process a job based on its type"""
        try:
            logger.info(f"Starting job processing: {job_id} ({job_type})")
            
            # Update job status to processing
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=10,
                progress_message="Starting processing..."
            )
            
            # Route to appropriate processor
            if job_type == "text_to_speech":
                result = await self._process_tts_job(job_id, input_data, user_id)
            elif job_type == "voice_clone":
                result = await self._process_voice_clone_job(job_id, input_data, user_id)
            elif job_type == "speech_translation":
                result = await self._process_translation_job(job_id, input_data, user_id)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Update job as completed
            await self.supabase_client.update_job_status(
                job_id,
                "completed",
                progress=100,
                progress_message="Processing completed",
                result_data=result
            )
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            
            # Update job as failed
            await self.supabase_client.update_job_status(
                job_id,
                "failed",
                progress=0,
                progress_message=f"Processing failed: {str(e)}",
                error_code="PROCESSING_ERROR",
                error_message=str(e)
            )
    
    async def _process_tts_job(self, job_id: str, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process text-to-speech job"""
        try:
            text = input_data.get("text", "")
            language = input_data.get("language", "en")
            voice_id = input_data.get("voice_id", "default")
            emotion = input_data.get("emotion", "neutral")
            speed = input_data.get("speed", 1.0)
            pitch = input_data.get("pitch", 1.0)
            
            if not text:
                raise ValueError("No text provided for TTS")
            
            # Update progress
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=30,
                progress_message="Generating speech..."
            )
            
            # Generate speech
            audio_data = await self.tts_engine.synthesize_speech(
                text=text,
                voice_id=voice_id,
                language=language,
                emotion=emotion,
                speed=speed,
                pitch=pitch
            )
            
            # Update progress
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=70,
                progress_message="Uploading audio..."
            )
            
            # Upload to storage
            audio_url = await self.supabase_client.upload_audio(
                audio_data, 
                f"{user_id}/{job_id}.wav"
            )
            
            # Update progress
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=90,
                progress_message="Finalizing..."
            )
            
            return {
                "audio_url": audio_url,
                "duration_ms": len(audio_data) // 48,  # Rough estimate
                "text": text,
                "voice_id": voice_id,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"TTS job processing failed: {str(e)}")
            raise
    
    async def _process_voice_clone_job(self, job_id: str, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process voice cloning job"""
        try:
            text = input_data.get("text", "")
            audio_sample = input_data.get("audio_sample")  # Base64 encoded
            
            if not text or not audio_sample:
                raise ValueError("Text and audio sample required for voice cloning")
            
            # Decode audio sample
            audio_bytes = base64.b64decode(audio_sample)
            
            # Update progress
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=40,
                progress_message="Cloning voice..."
            )
            
            # Clone voice
            cloned_audio = await self.tts_engine.clone_voice(audio_bytes, text)
            
            # Update progress
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=80,
                progress_message="Uploading result..."
            )
            
            # Upload result
            audio_url = await self.supabase_client.upload_audio(
                cloned_audio, 
                f"{user_id}/cloned/{job_id}.wav"
            )
            
            return {
                "audio_url": audio_url,
                "duration_ms": len(cloned_audio) // 48,
                "text": text,
                "voice_type": "cloned"
            }
            
        except Exception as e:
            logger.error(f"Voice clone job processing failed: {str(e)}")
            raise
    
    async def _process_translation_job(self, job_id: str, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process speech translation job"""
        try:
            # Placeholder for speech translation
            # This would integrate with Whisper for transcription and translation
            
            await self.supabase_client.update_job_status(
                job_id, 
                "processing", 
                progress=50,
                progress_message="Transcribing audio..."
            )
            
            # TODO: Implement Whisper integration
            original_text = "Placeholder transcription"
            translated_text = "Placeholder translation"
            
            # Generate TTS for translated text
            audio_data = await self.tts_engine.synthesize_speech(
                text=translated_text,
                language=input_data.get("target_language", "en")
            )
            
            # Upload result
            audio_url = await self.supabase_client.upload_audio(
                audio_data, 
                f"{user_id}/translated/{job_id}.wav"
            )
            
            return {
                "original_text": original_text,
                "translated_text": translated_text,
                "audio_url": audio_url,
                "source_language": "auto",
                "target_language": input_data.get("target_language", "en")
            }
            
        except Exception as e:
            logger.error(f"Translation job processing failed: {str(e)}")
            raise