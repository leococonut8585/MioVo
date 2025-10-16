"""
Pydantic models for FastAPI Gateway
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Task type enum"""
    TTS = "tts"
    RVC = "rvc"
    SEPARATION = "separation"


class TaskStatus(str, Enum):
    """Task status enum"""
    IDLE = "idle"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TTSRequest(BaseModel):
    """Text-to-speech request"""
    text: str = Field(..., min_length=1, max_length=10000)
    speaker_id: int = Field(..., ge=0)
    speed_scale: float = Field(1.0, ge=0.5, le=2.0)
    pitch_scale: float = Field(0.0, ge=-1.0, le=1.0)
    intonation_scale: float = Field(1.0, ge=0.0, le=2.0)
    volume_scale: float = Field(1.0, ge=0.0, le=2.0)


class RVCRequest(BaseModel):
    """Voice conversion request"""
    audio_base64: str
    model_name: str
    f0method: str = Field("rmvpe", pattern="^(harvest|rmvpe|crepe|pm)$")
    protect: float = Field(0.5, ge=0.0, le=0.5)
    index_rate: float = Field(0.75, ge=0.0, le=1.0)
    filter_radius: int = Field(3, ge=0, le=7)


class SeparationRequest(BaseModel):
    """Vocal separation request"""
    audio_base64: str
    model: str = Field("htdemucs", description="Demucs model preset")


class TaskResponse(BaseModel):
    """Task response"""
    task_id: str
    type: TaskType
    status: TaskStatus
    progress: float = Field(0.0, ge=0.0, le=100.0)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    aivisspeech: bool = False
    rvc: bool = False
