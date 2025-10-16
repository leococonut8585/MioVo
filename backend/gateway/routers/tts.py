"""
TTS Router - Text-to-Speech endpoints
Integrates with AivisSpeech Engine
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import base64
import uuid
from datetime import datetime
from loguru import logger
import io
import struct
import wave

from models import TTSRequest, TaskResponse, TaskType, TaskStatus
# Note: AivisSpeech service needs to be running separately
# from aivisspeech.client import AivisSpeechClient


# Batch TTS Request Model
class BatchTTSRequest(BaseModel):
    """Batch text-to-speech request"""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    speaker_id: int = Field(..., ge=0)
    speed_scale: float = Field(1.0, ge=0.5, le=2.0)
    pitch_scale: float = Field(0.0, ge=-1.0, le=1.0)
    intonation_scale: float = Field(1.0, ge=0.0, le=2.0)
    volume_scale: float = Field(1.0, ge=0.0, le=2.0)


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


def create_mock_wav_data(duration_seconds: float = 0.5, sample_rate: int = 44100) -> bytes:
    """Create mock WAV audio data for testing in Replit environment"""
    # Generate silence (could be replaced with actual audio generation)
    num_samples = int(duration_seconds * sample_rate)
    samples = struct.pack('<' + 'h' * num_samples, *([0] * num_samples))
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples)
    
    wav_buffer.seek(0)
    return wav_buffer.read()


def concatenate_wav_files(wav_data_list: List[bytes]) -> bytes:
    """Concatenate multiple WAV files into one"""
    if not wav_data_list:
        return create_mock_wav_data()
    
    # Parse first WAV to get parameters
    first_wav = io.BytesIO(wav_data_list[0])
    with wave.open(first_wav, 'rb') as wav:
        params = wav.getparams()
        sample_rate = params.framerate
        num_channels = params.nchannels
        sample_width = params.sampwidth
    
    # Collect all audio samples
    all_samples = []
    for wav_data in wav_data_list:
        wav_buffer = io.BytesIO(wav_data)
        with wave.open(wav_buffer, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            all_samples.append(frames)
    
    # Concatenate all samples
    concatenated_samples = b''.join(all_samples)
    
    # Create output WAV
    output_buffer = io.BytesIO()
    with wave.open(output_buffer, 'wb') as out_wav:
        out_wav.setnchannels(num_channels)
        out_wav.setsampwidth(sample_width)
        out_wav.setframerate(sample_rate)
        out_wav.writeframes(concatenated_samples)
    
    output_buffer.seek(0)
    return output_buffer.read()


@router.post("/synthesize_batch")
async def synthesize_batch(request: BatchTTSRequest):
    """
    Synthesize speech for multiple texts in batch
    
    Args:
        request: Batch TTS parameters
        
    Returns:
        Concatenated WAV audio stream
    """
    try:
        logger.info(f"Batch synthesis requested for {len(request.texts)} texts")
        
        # In Replit environment, generate mock audio for each text
        # In production, this would call the actual AivisSpeech Engine
        wav_data_list = []
        
        for i, text in enumerate(request.texts):
            logger.debug(f"Processing text {i+1}/{len(request.texts)}: {text[:50]}...")
            
            # Mock audio generation
            # Duration varies by text length and speed scale
            base_duration = min(len(text) * 0.05, 5.0)  # Estimate ~50ms per character, max 5s
            adjusted_duration = base_duration / request.speed_scale
            
            # Create mock WAV data
            wav_data = create_mock_wav_data(duration_seconds=adjusted_duration)
            wav_data_list.append(wav_data)
        
        # Concatenate all WAV files
        combined_wav = concatenate_wav_files(wav_data_list)
        
        logger.info(f"Successfully generated batch audio for {len(request.texts)} texts")
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(combined_wav),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=batch_synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"Batch synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
