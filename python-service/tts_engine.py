import os
import torch
import numpy as np
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import soundfile as sf
import logging
from typing import Optional, Dict, Any
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sample_rate = 24000
        self.models_cache = {}
        
    async def initialize(self):
        """Initialize TTS models"""
        try:
            logger.info(f"Initializing TTS engine on {self.device}")
            
            # Initialize default XTTS model
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            raise
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice_id: str = "default",
        language: str = "en",
        emotion: str = "neutral",
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> bytes:
        """Synthesize speech from text"""
        try:
            logger.info(f"Synthesizing speech: {len(text)} chars, voice={voice_id}, lang={language}")
            
            # Clean and prepare text
            text = self._prepare_text(text)
            
            # Get voice settings
            voice_settings = self._get_voice_settings(voice_id, emotion, speed, pitch)
            
            # Generate audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                if hasattr(self.model, 'tts_to_file'):
                    # XTTS model
                    self.model.tts_to_file(
                        text=text,
                        file_path=tmp_file.name,
                        speaker_wav=voice_settings.get("speaker_wav"),
                        language=language
                    )
                else:
                    # Fallback for other models
                    wav = self.model.tts(text=text, language=language)
                    sf.write(tmp_file.name, wav, self.sample_rate)
                
                # Read generated audio
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                # Cleanup
                os.unlink(tmp_file.name)
                
                logger.info(f"Speech synthesis completed: {len(audio_data)} bytes")
                return audio_data
                
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise
    
    def _prepare_text(self, text: str) -> str:
        """Clean and prepare text for TTS"""
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Ensure text ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def _get_voice_settings(self, voice_id: str, emotion: str, speed: float, pitch: float) -> Dict[str, Any]:
        """Get voice configuration settings"""
        settings = {
            "speaker_wav": None,  # Default voice
            "emotion": emotion,
            "speed": speed,
            "pitch": pitch
        }
        
        # Map voice IDs to speaker files (when available)
        voice_mapping = {
            "default": None,
            "female-1": None,  # Will use default for now
            "male-1": None,    # Will use default for now
        }
        
        settings["speaker_wav"] = voice_mapping.get(voice_id)
        return settings
    
    async def clone_voice(self, audio_file: bytes, text: str) -> bytes:
        """Clone voice from audio sample"""
        try:
            logger.info("Starting voice cloning process")
            
            # Save audio sample temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as sample_file:
                sample_file.write(audio_file)
                sample_path = sample_file.name
            
            # Generate speech with cloned voice
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
                self.model.tts_to_file(
                    text=text,
                    file_path=output_file.name,
                    speaker_wav=sample_path,
                    language="en"
                )
                
                # Read result
                with open(output_file.name, 'rb') as f:
                    cloned_audio = f.read()
            
            # Cleanup
            os.unlink(sample_path)
            os.unlink(output_file.name)
            
            logger.info("Voice cloning completed successfully")
            return cloned_audio
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up TTS engine resources")
        if self.model:
            del self.model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None