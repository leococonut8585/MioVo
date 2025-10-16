"""
RVC Router - Voice Conversion endpoints
Integrates with RVC Service (Docker)
"""
from fastapi import APIRouter, HTTPException
import httpx
import uuid
from datetime import datetime
from loguru import logger

from models import RVCRequest, TaskResponse, TaskType, TaskStatus

router = APIRouter(prefix="/rvc", tags=["rvc"])

# RVC service URL (Docker container)
RVC_SERVICE_URL = "http://localhost:10102"


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
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Set parameters
            params_response = await client.post(
                f"{RVC_SERVICE_URL}/params",
                json={
                    "f0method": request.f0method,
                    "protect": request.protect,
                    "index_rate": request.index_rate,
                    "filter_radius": request.filter_radius
                }
            )
            params_response.raise_for_status()
            
            # Convert
            convert_response = await client.post(
                f"{RVC_SERVICE_URL}/convert",
                json={
                    "audio_base64": request.audio_base64,
                    "model_name": request.model_name,
                    "params": {
                        "f0method": request.f0method,
                        "protect": request.protect,
                        "index_rate": request.index_rate,
                        "filter_radius": request.filter_radius
                    }
                }
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
                    "model": request.model_name
                },
                created_at=now,
                updated_at=datetime.utcnow()
            )
            
    except httpx.HTTPError as e:
        logger.error(f"RVC conversion failed: {e}")
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
        logger.error(f"Unexpected error in RVC conversion: {e}")
        return TaskResponse(
            task_id=task_id,
            type=TaskType.RVC,
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{RVC_SERVICE_URL}/models")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get RVC models: {e}")
        raise HTTPException(status_code=503, detail="RVC service unavailable")


@router.post("/models/{model_name}")
async def load_model(model_name: str):
    """Load RVC model into memory"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{RVC_SERVICE_URL}/models/{model_name}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check RVC service health"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{RVC_SERVICE_URL}/health")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"RVC health check failed: {e}")
        return {
            "rvc": False,
            "status": "unhealthy",
            "error": str(e)
        }
