"""
TTS Router - Text-to-Speech endpoints
Integrates with AivisSpeech Engine
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import base64
import uuid
from datetime import datetime
from loguru import logger

from models import TTSRequest, TaskResponse, TaskType, TaskStatus
# Note: AivisSpeech service needs to be running separately
# from aivisspeech.client import AivisSpeechClient

router = APIRouter(prefix="/tts", tags=["tts"])

# AivisSpeech client (singleton) - Disabled for Replit environment
# aivis_client = None

# async def get_aivis_client() -> AivisSpeechClient:
#     """Get or create AivisSpeech client"""
#     global aivis_client
#     if aivis_client is None:
#         aivis_client = AivisSpeechClient()
#     return aivis_client


@router.post("/synthesize", response_model=TaskResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text
    
    Args:
        request: TTS parameters
        
    Returns:
        Task with audio result (base64)
    """
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    try:
        # Note: AivisSpeech service is not available in Replit environment
        # This endpoint requires the full local setup with AivisSpeech Engine
        logger.warning(f"TTS service not available in cloud environment: {task_id}")
        
        return TaskResponse(
            task_id=task_id,
            type=TaskType.TTS,
            status=TaskStatus.FAILED,
            progress=0.0,
            error="TTS service (AivisSpeech) requires local setup. See README for installation instructions.",
            created_at=now,
            updated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.TTS,
            status=TaskStatus.FAILED,
            progress=0.0,
            error=str(e),
            created_at=now,
            updated_at=datetime.utcnow()
        )


@router.get("/speakers")
async def get_speakers():
    """Get available speakers/styles from AivisSpeech"""
    try:
        client = await get_aivis_client()
        speakers = await client.get_speakers()
        return {"speakers": speakers}
    except Exception as e:
        logger.error(f"Failed to get speakers: {e}")
        raise HTTPException(status_code=503, detail="AivisSpeech unavailable")


@router.get("/health")
async def health_check():
    """Check AivisSpeech Engine health"""
    try:
        client = await get_aivis_client()
        is_healthy = await client.health_check()
        return {
            "aivisspeech": is_healthy,
            "status": "healthy" if is_healthy else "degraded"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "aivisspeech": False,
            "status": "unhealthy",
            "error": str(e)
        }
