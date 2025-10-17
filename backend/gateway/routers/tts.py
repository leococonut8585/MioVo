"""
TTS Router - Text-to-Speech endpoints
Integrates with AivisSpeech Engine via Cloudflare Tunnel
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import base64
import uuid
from datetime import datetime
from loguru import logger
import io
import struct
import wave
import httpx
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TTSRequest, TaskResponse, TaskType, TaskStatus
from config import config


# Batch TTS Request Model
class BatchTTSRequest(BaseModel):
    """Batch text-to-speech request"""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    speaker_id: int = Field(..., ge=0)
    speed_scale: float = Field(1.0, ge=0.5, le=2.0)
    pitch_scale: float = Field(0.0, ge=-1.0, le=1.0)
    intonation_scale: float = Field(1.0, ge=0.0, le=2.0)
    volume_scale: float = Field(1.0, ge=0.0, le=2.0)


# Speaker Info Model
class SpeakerInfo(BaseModel):
    """Speaker information"""
    speaker_id: int
    name: str
    styles: List[Dict[str, Any]]


router = APIRouter(prefix="/tts", tags=["tts"])

# AivisSpeech client singleton
aivisspeech_client: Optional[httpx.AsyncClient] = None


async def get_aivisspeech_client() -> httpx.AsyncClient:
    """Get or create AivisSpeech client with Cloudflare Tunnel URL"""
    global aivisspeech_client
    if aivisspeech_client is None:
        aivisspeech_url = config.get_aivisspeech_url()
        logger.info(f"Initializing AivisSpeech client with URL: {aivisspeech_url}")
        aivisspeech_client = httpx.AsyncClient(
            base_url=aivisspeech_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=30.0,
                pool=30.0
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            )
        )
    return aivisspeech_client


@router.post("/synthesize", response_model=TaskResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text using AivisSpeech Engine
    
    Args:
        request: TTS parameters
        
    Returns:
        Task with audio result (base64)
    """
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    try:
        if not config.ENABLE_REAL_SERVICES:
            # Fallback to mock mode
            logger.warning(f"Real services disabled. Using mock TTS for task: {task_id}")
            wav_data = create_mock_wav_data(duration_seconds=2.0)
            audio_base64 = base64.b64encode(wav_data).decode('utf-8')
            
            return TaskResponse(
                task_id=task_id,
                type=TaskType.TTS,
                status=TaskStatus.COMPLETED,
                progress=100.0,
                result={
                    "audio_base64": audio_base64,
                    "speaker_id": request.speaker_id,
                    "mock": True
                },
                created_at=now,
                updated_at=datetime.utcnow()
            )
        
        # Connect to real AivisSpeech service
        client = await get_aivisspeech_client()
        
        # Step 1: Create audio query
        logger.info(f"Creating audio query for task {task_id}")
        query_response = await client.post(
            "/audio_query",
            params={
                "text": request.text,
                "speaker": request.speaker_id
            }
        )
        query_response.raise_for_status()
        audio_query = query_response.json()
        
        # Step 2: Apply TTS parameters
        audio_query['speedScale'] = request.speed_scale
        audio_query['pitchScale'] = request.pitch_scale
        audio_query['intonationScale'] = request.intonation_scale
        audio_query['volumeScale'] = request.volume_scale
        
        # Step 3: Synthesize audio
        logger.info(f"Synthesizing audio for task {task_id}")
        synthesis_response = await client.post(
            "/synthesis",
            params={"speaker": request.speaker_id},
            json=audio_query,
            headers={"Content-Type": "application/json"}
        )
        synthesis_response.raise_for_status()
        
        # Get WAV audio data
        wav_data = synthesis_response.content
        audio_base64 = base64.b64encode(wav_data).decode('utf-8')
        
        logger.info(f"TTS synthesis completed: {task_id}")
        
        return TaskResponse(
            task_id=task_id,
            type=TaskType.TTS,
            status=TaskStatus.COMPLETED,
            progress=100.0,
            result={
                "audio_base64": audio_base64,
                "speaker_id": request.speaker_id,
                "text_length": len(request.text)
            },
            created_at=now,
            updated_at=datetime.utcnow()
        )
        
    except httpx.HTTPError as e:
        logger.error(f"AivisSpeech API error for task {task_id}: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.TTS,
            status=TaskStatus.FAILED,
            progress=0.0,
            error=f"AivisSpeech service error: {str(e)}",
            created_at=now,
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"TTS synthesis failed for task {task_id}: {e}")
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
        if not config.ENABLE_REAL_SERVICES:
            # Return mock speakers
            return {
                "speakers": [
                    {"speaker_id": 0, "name": "Default", "styles": []},
                    {"speaker_id": 1, "name": "Female", "styles": []},
                    {"speaker_id": 2, "name": "Male", "styles": []}
                ]
            }
        
        client = await get_aivisspeech_client()
        response = await client.get("/speakers")
        response.raise_for_status()
        
        return {"speakers": response.json()}
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to get speakers from AivisSpeech: {e}")
        raise HTTPException(status_code=503, detail="AivisSpeech service unavailable")
    except Exception as e:
        logger.error(f"Failed to get speakers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check AivisSpeech Engine health"""
    try:
        start_time = time.time()
        
        if not config.ENABLE_REAL_SERVICES:
            return {
                "aivisspeech": True,
                "status": "mock",
                "response_time_ms": 0,
                "service_url": "mock://localhost"
            }
        
        client = await get_aivisspeech_client()
        response = await client.get("/speakers", timeout=5.0)
        is_healthy = response.status_code == 200
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "aivisspeech": is_healthy,
            "status": "healthy" if is_healthy else "degraded",
            "response_time_ms": round(response_time, 2),
            "service_url": config.get_aivisspeech_url()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "aivisspeech": False,
            "status": "unhealthy",
            "error": str(e),
            "service_url": config.get_aivisspeech_url()
        }


@router.get("/test_connection")
async def test_connection():
    """Test connection to AivisSpeech service"""
    try:
        if not config.ENABLE_REAL_SERVICES:
            return {
                "connected": True,
                "service": "AivisSpeech (Mock Mode)",
                "url": "mock://localhost",
                "message": "Running in mock mode. Set ENABLE_REAL_SERVICES=true to connect to real service."
            }
        
        client = await get_aivisspeech_client()
        url = config.get_aivisspeech_url()
        
        # Try to get speakers as a connection test
        start_time = time.time()
        response = await client.get("/speakers", timeout=10.0)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            speakers = response.json()
            return {
                "connected": True,
                "service": "AivisSpeech",
                "url": url,
                "response_time_ms": round(response_time, 2),
                "speakers_available": len(speakers) if isinstance(speakers, list) else 0,
                "message": "Successfully connected to AivisSpeech service"
            }
        else:
            return {
                "connected": False,
                "service": "AivisSpeech",
                "url": url,
                "error": f"Unexpected status code: {response.status_code}",
                "message": "Service responded but with unexpected status"
            }
            
    except httpx.ConnectError as e:
        return {
            "connected": False,
            "service": "AivisSpeech",
            "url": config.get_aivisspeech_url(),
            "error": "Connection refused",
            "message": f"Cannot connect to AivisSpeech at {config.get_aivisspeech_url()}. Ensure the service is running and accessible."
        }
    except httpx.TimeoutException as e:
        return {
            "connected": False,
            "service": "AivisSpeech",
            "url": config.get_aivisspeech_url(),
            "error": "Connection timeout",
            "message": "Connection timed out. The service may be slow or unreachable."
        }
    except Exception as e:
        return {
            "connected": False,
            "service": "AivisSpeech",
            "url": config.get_aivisspeech_url(),
            "error": str(e),
            "message": "An unexpected error occurred while testing the connection"
        }


def create_mock_wav_data(duration_seconds: float = 0.5, sample_rate: int = 44100) -> bytes:
    """Create mock WAV audio data for testing"""
    # Generate silence
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
        
        wav_data_list = []
        
        if not config.ENABLE_REAL_SERVICES:
            # Mock mode: generate silent audio
            for i, text in enumerate(request.texts):
                logger.debug(f"Generating mock audio {i+1}/{len(request.texts)}")
                base_duration = min(len(text) * 0.05, 5.0)
                adjusted_duration = base_duration / request.speed_scale
                wav_data = create_mock_wav_data(duration_seconds=adjusted_duration)
                wav_data_list.append(wav_data)
        else:
            # Real mode: use AivisSpeech API
            client = await get_aivisspeech_client()
            
            for i, text in enumerate(request.texts):
                logger.debug(f"Synthesizing text {i+1}/{len(request.texts)}: {text[:50]}...")
                
                try:
                    # Create audio query
                    query_response = await client.post(
                        "/audio_query",
                        params={
                            "text": text,
                            "speaker": request.speaker_id
                        }
                    )
                    query_response.raise_for_status()
                    audio_query = query_response.json()
                    
                    # Apply parameters
                    audio_query['speedScale'] = request.speed_scale
                    audio_query['pitchScale'] = request.pitch_scale
                    audio_query['intonationScale'] = request.intonation_scale
                    audio_query['volumeScale'] = request.volume_scale
                    
                    # Synthesize
                    synthesis_response = await client.post(
                        "/synthesis",
                        params={"speaker": request.speaker_id},
                        json=audio_query,
                        headers={"Content-Type": "application/json"}
                    )
                    synthesis_response.raise_for_status()
                    
                    wav_data_list.append(synthesis_response.content)
                    
                except Exception as e:
                    logger.error(f"Failed to synthesize text {i+1}: {e}")
                    # Add silence for failed synthesis
                    wav_data_list.append(create_mock_wav_data(duration_seconds=0.5))
        
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