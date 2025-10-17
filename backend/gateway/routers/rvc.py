"""
RVC Router - Voice Conversion endpoints
Integrates with RVC Service via Cloudflare Tunnel
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import httpx
import uuid
from datetime import datetime
from loguru import logger
import base64
import time
import sys
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import io

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import RVCRequest, TaskResponse, TaskType, TaskStatus
from config import config

router = APIRouter(prefix="/rvc", tags=["rvc"])

# RVC client singleton
rvc_client: Optional[httpx.AsyncClient] = None


# Separation Request Model
class SeparationRequest(BaseModel):
    """Vocal separation request"""
    audio_base64: str
    model: str = Field("htdemucs", description="Separation model")
    shifts: int = Field(1, ge=1, le=5, description="Number of prediction shifts")
    overlap: float = Field(0.25, ge=0.0, le=0.5, description="Overlap ratio")


async def get_rvc_client() -> httpx.AsyncClient:
    """Get or create RVC client with Cloudflare Tunnel URL"""
    global rvc_client
    if rvc_client is None:
        rvc_url = config.get_rvc_url()
        logger.info(f"Initializing RVC client with URL: {rvc_url}")
        rvc_client = httpx.AsyncClient(
            base_url=rvc_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=120.0,  # Longer timeout for processing
                write=120.0,
                pool=120.0
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            )
        )
    return rvc_client


@router.post("/convert", response_model=TaskResponse)
async def convert_voice(request: RVCRequest):
    """
    Convert voice using RVC
    
    Args:
        request: Audio + model + parameters
        
    Returns:
        Task with converted audio (base64)
    """
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    try:
        if not config.ENABLE_REAL_SERVICES:
            # Mock mode
            logger.warning(f"Real services disabled. Using mock RVC for task: {task_id}")
            return TaskResponse(
                task_id=task_id,
                type=TaskType.RVC,
                status=TaskStatus.COMPLETED,
                progress=100.0,
                result={
                    "audio_base64": request.audio_base64,  # Return original audio in mock mode
                    "model": request.model_name,
                    "mock": True
                },
                created_at=now,
                updated_at=datetime.utcnow()
            )
        
        # Connect to real RVC service
        client = await get_rvc_client()
        
        # Prepare conversion request
        conversion_data = {
            "audio_base64": request.audio_base64,
            "model_name": request.model_name,
            "f0method": request.f0method,
            "protect": request.protect,
            "index_rate": request.index_rate,
            "filter_radius": request.filter_radius
        }
        
        logger.info(f"Starting RVC conversion for task {task_id} with model {request.model_name}")
        
        # Send conversion request
        convert_response = await client.post(
            "/convert",
            json=conversion_data
        )
        convert_response.raise_for_status()
        result_data = convert_response.json()
        
        logger.info(f"RVC conversion completed: {task_id}")
        
        return TaskResponse(
            task_id=task_id,
            type=TaskType.RVC,
            status=TaskStatus.COMPLETED,
            progress=100.0,
            result={
                "audio_base64": result_data.get("audio_base64"),
                "model": request.model_name,
                "processing_time": result_data.get("processing_time", 0)
            },
            created_at=now,
            updated_at=datetime.utcnow()
        )
        
    except httpx.HTTPError as e:
        logger.error(f"RVC API error for task {task_id}: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.RVC,
            status=TaskStatus.FAILED,
            progress=0.0,
            error=f"RVC service error: {str(e)}",
            created_at=now,
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Unexpected error in RVC conversion for task {task_id}: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.RVC,
            status=TaskStatus.FAILED,
            progress=0.0,
            error=str(e),
            created_at=now,
            updated_at=datetime.utcnow()
        )


@router.post("/separate", response_model=TaskResponse)
async def separate_vocals(request: SeparationRequest):
    """
    Separate vocals from audio using Demucs
    
    Args:
        request: Audio + separation parameters
        
    Returns:
        Task with separated audio tracks (vocals and instrumental)
    """
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    try:
        if not config.ENABLE_REAL_SERVICES:
            # Mock mode
            logger.warning(f"Real services disabled. Using mock separation for task: {task_id}")
            return TaskResponse(
                task_id=task_id,
                type=TaskType.SEPARATION,
                status=TaskStatus.COMPLETED,
                progress=100.0,
                result={
                    "vocals_base64": request.audio_base64,
                    "instrumental_base64": request.audio_base64,
                    "mock": True
                },
                created_at=now,
                updated_at=datetime.utcnow()
            )
        
        # Connect to RVC service (which includes Demucs)
        client = await get_rvc_client()
        
        # Prepare separation request
        separation_data = {
            "audio_base64": request.audio_base64,
            "model": request.model,
            "shifts": request.shifts,
            "overlap": request.overlap
        }
        
        logger.info(f"Starting vocal separation for task {task_id} with model {request.model}")
        
        # Send separation request
        separate_response = await client.post(
            "/separate",
            json=separation_data
        )
        separate_response.raise_for_status()
        result_data = separate_response.json()
        
        logger.info(f"Vocal separation completed: {task_id}")
        
        return TaskResponse(
            task_id=task_id,
            type=TaskType.SEPARATION,
            status=TaskStatus.COMPLETED,
            progress=100.0,
            result={
                "vocals_base64": result_data.get("vocals_base64"),
                "instrumental_base64": result_data.get("instrumental_base64"),
                "processing_time": result_data.get("processing_time", 0)
            },
            created_at=now,
            updated_at=datetime.utcnow()
        )
        
    except httpx.HTTPError as e:
        logger.error(f"Separation API error for task {task_id}: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.SEPARATION,
            status=TaskStatus.FAILED,
            progress=0.0,
            error=f"Separation service error: {str(e)}",
            created_at=now,
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Unexpected error in vocal separation for task {task_id}: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.SEPARATION,
            status=TaskStatus.FAILED,
            progress=0.0,
            error=str(e),
            created_at=now,
            updated_at=datetime.utcnow()
        )


@router.get("/models")
async def get_models():
    """Get available RVC models"""
    try:
        if not config.ENABLE_REAL_SERVICES:
            # Return mock models
            return {
                "models": [
                    {"name": "leo_model", "description": "Leo Voice Model", "size": "50MB"},
                    {"name": "default_model", "description": "Default RVC Model", "size": "45MB"}
                ]
            }
        
        client = await get_rvc_client()
        response = await client.get("/models")
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to get RVC models: {e}")
        raise HTTPException(status_code=503, detail="RVC service unavailable")
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/load")
async def load_model(model_name: str):
    """Load RVC model into memory"""
    try:
        if not config.ENABLE_REAL_SERVICES:
            return {
                "success": True,
                "model": model_name,
                "message": f"Mock: Model {model_name} loaded"
            }
        
        client = await get_rvc_client()
        response = await client.post(f"/models/{model_name}/load")
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to load model: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check RVC service health"""
    try:
        start_time = time.time()
        
        if not config.ENABLE_REAL_SERVICES:
            return {
                "rvc": True,
                "status": "mock",
                "response_time_ms": 0,
                "service_url": "mock://localhost"
            }
        
        client = await get_rvc_client()
        response = await client.get("/health", timeout=5.0)
        is_healthy = response.status_code == 200
        
        response_time = (time.time() - start_time) * 1000
        
        result = response.json() if is_healthy else {}
        
        return {
            "rvc": is_healthy,
            "status": "healthy" if is_healthy else "degraded",
            "response_time_ms": round(response_time, 2),
            "service_url": config.get_rvc_url(),
            "models_loaded": result.get("models_loaded", 0),
            "gpu_available": result.get("gpu_available", False)
        }
    except Exception as e:
        logger.error(f"RVC health check failed: {e}")
        return {
            "rvc": False,
            "status": "unhealthy",
            "error": str(e),
            "service_url": config.get_rvc_url()
        }


@router.get("/test_connection")
async def test_connection():
    """Test connection to RVC service"""
    try:
        if not config.ENABLE_REAL_SERVICES:
            return {
                "connected": True,
                "service": "RVC (Mock Mode)",
                "url": "mock://localhost",
                "message": "Running in mock mode. Set ENABLE_REAL_SERVICES=true to connect to real service."
            }
        
        client = await get_rvc_client()
        url = config.get_rvc_url()
        
        # Try health check as connection test
        start_time = time.time()
        response = await client.get("/health", timeout=10.0)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            health_data = response.json()
            return {
                "connected": True,
                "service": "RVC",
                "url": url,
                "response_time_ms": round(response_time, 2),
                "gpu_available": health_data.get("gpu_available", False),
                "models_loaded": health_data.get("models_loaded", 0),
                "message": "Successfully connected to RVC service"
            }
        else:
            return {
                "connected": False,
                "service": "RVC",
                "url": url,
                "error": f"Unexpected status code: {response.status_code}",
                "message": "Service responded but with unexpected status"
            }
            
    except httpx.ConnectError as e:
        return {
            "connected": False,
            "service": "RVC",
            "url": config.get_rvc_url(),
            "error": "Connection refused",
            "message": f"Cannot connect to RVC at {config.get_rvc_url()}. Ensure the service is running and accessible."
        }
    except httpx.TimeoutException as e:
        return {
            "connected": False,
            "service": "RVC",
            "url": config.get_rvc_url(),
            "error": "Connection timeout",
            "message": "Connection timed out. The service may be slow or unreachable."
        }
    except Exception as e:
        return {
            "connected": False,
            "service": "RVC",
            "url": config.get_rvc_url(),
            "error": str(e),
            "message": "An unexpected error occurred while testing the connection"
        }


@router.get("/gpu_info")
async def get_gpu_info():
    """Get GPU information from RVC service"""
    try:
        if not config.ENABLE_REAL_SERVICES:
            return {
                "gpu_available": True,
                "gpu_name": "NVIDIA GeForce RTX 5090 (Mock)",
                "cuda_version": "12.1",
                "vram_total": "32GB",
                "vram_used": "4GB",
                "mock": True
            }
        
        client = await get_rvc_client()
        response = await client.get("/gpu_info")
        response.raise_for_status()
        return response.json()
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to get GPU info: {e}")
        return {
            "gpu_available": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Failed to get GPU info: {e}")
        return {
            "gpu_available": False,
            "error": str(e)
        }