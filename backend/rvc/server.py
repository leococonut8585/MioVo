"""
RVC API Server
Voice Conversion Service
Port: 10102
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import base64
import io
import uvicorn
from loguru import logger

# RVC imports
try:
    from rvc_python import RVC
    RVC_AVAILABLE = True
except ImportError:
    logger.warning("rvc-python not installed, running in API-only mode")
    RVC_AVAILABLE = False
    RVC = None

app = FastAPI(
    title="MioVo RVC Service",
    description="Voice Conversion API using RVC",
    version="0.1.0"
)

# Global state for RVC service
rvc_instance = None
current_model = None
current_params = None
model_cache = {}  # LRU cache for loaded models (max 5-7 models)
MAX_CACHE_SIZE = 7


def init_rvc():
    """Initialize RVC instance"""
    global rvc_instance
    if RVC_AVAILABLE and rvc_instance is None:
        import os
        device = os.getenv("RVC_DEVICE", "cuda:0")
        logger.info(f"Initializing RVC with device: {device}")
        rvc_instance = RVC(device=device)
    return rvc_instance


class RVCParams(BaseModel):
    """RVC conversion parameters"""
    f0method: str = "rmvpe"  # harvest, rmvpe, crepe, pm
    protect: float = 0.5     # 0.0-0.5
    index_rate: float = 0.75
    filter_radius: int = 3
    resample_sr: int = 0     # 0=auto
    rms_mix_rate: float = 0.25


class ConvertRequest(BaseModel):
    """Voice conversion request"""
    audio_base64: str
    model_name: str
    params: Optional[RVCParams] = None


class SeparationRequest(BaseModel):
    """Vocal separation request"""
    audio_base64: str
    model: str = "htdemucs"  # Demucs model preset


def separate_vocals(audio_path: str, output_dir: str) -> tuple[str, str]:
    """
    Separate vocals from audio using Demucs v4
    
    Args:
        audio_path: Input audio file path
        output_dir: Output directory
        
    Returns:
        (vocals_path, accompaniment_path)
    """
    import subprocess
    import os
    
    logger.info(f"Separating vocals with Demucs: {audio_path}")
    
    try:
        # Run Demucs
        subprocess.run([
            "demucs",
            "--two-stems=vocals",
            "-o", output_dir,
            audio_path
        ], check=True, capture_output=True, text=True)
        
        # Find output files
        # Demucs creates: output_dir/htdemucs/{filename}/vocals.wav, no_vocals.wav
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        vocals_path = os.path.join(output_dir, "htdemucs", base_name, "vocals.wav")
        accompaniment_path = os.path.join(output_dir, "htdemucs", base_name, "no_vocals.wav")
        
        if not os.path.exists(vocals_path):
            raise FileNotFoundError(f"Vocals not found: {vocals_path}")
        
        logger.info(f"Separation completed: vocals={vocals_path}")
        
        return vocals_path, accompaniment_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Demucs failed: {e.stderr}")
        raise RuntimeError(f"Demucs separation failed: {e.stderr}")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "miovo-rvc",
        "version": "0.1.0",
        "rvc_loaded": current_model is not None,
        "current_model": current_model
    }


# Get available models
@app.get("/models")
async def get_models():
    """Get list of available RVC models"""
    import os
    model_dir = os.getenv("RVC_MODEL_DIR", "/models")
    
    try:
        if os.path.exists(model_dir):
            # Scan for .pth files
            models = [
                f for f in os.listdir(model_dir)
                if f.endswith('.pth')
            ]
            return {"models": models, "count": len(models)}
        return {"models": [], "count": 0}
    except Exception as e:
        logger.error(f"Failed to scan models: {e}")
        return {"models": [], "error": str(e)}


# Load model
@app.post("/models/{model_name}")
async def load_model(model_name: str):
    """Load RVC model into memory (LRU cache)"""
    global current_model, model_cache
    
    if not RVC_AVAILABLE:
        raise HTTPException(status_code=503, detail="RVC not available")
    
    try:
        import os
        import torch
        
        logger.info(f"Loading model: {model_name}")
        
        # Initialize RVC if needed
        rvc = init_rvc()
        if not rvc:
            raise HTTPException(status_code=500, detail="Failed to initialize RVC")
        
        # Model path
        model_dir = os.getenv("RVC_MODEL_DIR", "/models")
        model_path = os.path.join(model_dir, model_name)
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
        
        # Load model using rvc-python
        rvc.load_model(model_path)
        
        # Update cache (LRU)
        if len(model_cache) >= MAX_CACHE_SIZE:
            # Remove oldest
            oldest_key = next(iter(model_cache))
            del model_cache[oldest_key]
            torch.cuda.empty_cache()
            logger.info(f"Evicted model from cache: {oldest_key}")
        
        model_cache[model_name] = {"loaded_at": datetime.utcnow().isoformat()}
        current_model = model_name
        
        logger.info(f"Model loaded successfully: {model_name}")
        
        return {
            "status": "loaded",
            "model": model_name,
            "cache_size": len(model_cache)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Set parameters
@app.post("/params")
async def set_params(params: RVCParams):
    """Set RVC conversion parameters"""
    global current_params
    
    try:
        current_params = params
        logger.info(f"Parameters set: {params}")
        
        return {
            "status": "parameters_set",
            "params": params.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get parameters
@app.get("/params")
async def get_params():
    """Get current RVC parameters"""
    if current_params:
        return current_params.dict()
    default_params = RVCParams()
    return default_params.dict()


# Convert voice
@app.post("/convert")
async def convert_voice(request: ConvertRequest):
    """
    Convert voice using RVC
    
    Args:
        request: Audio data (base64) + model name + parameters
        
    Returns:
        Converted audio (base64)
    """
    if not RVC_AVAILABLE:
        raise HTTPException(status_code=503, detail="RVC not available")
    
    try:
        import os
        import tempfile
        import soundfile as sf
        import numpy as np
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_base64)
        
        logger.info(f"Converting with model: {request.model_name}")
        
        # Initialize RVC if needed
        rvc = init_rvc()
        if not rvc:
            raise HTTPException(status_code=500, detail="Failed to initialize RVC")
        
        # Load model if different from current
        if current_model != request.model_name:
            model_dir = os.getenv("RVC_MODEL_DIR", "/models")
            model_path = os.path.join(model_dir, request.model_name)
            if not os.path.exists(model_path):
                raise HTTPException(status_code=404, detail=f"Model not found: {request.model_name}")
            rvc.load_model(model_path)
        
        # Use request params if provided, otherwise use global current_params
        params = request.params or current_params or RVCParams()
        
        logger.info(f"Using params: f0method={params.f0method}, protect={params.protect}")
        
        # Write input audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as input_file:
            input_path = input_file.name
            input_file.write(audio_bytes)
        
        # Output temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Perform RVC conversion
            rvc.infer_file(
                input_path=input_path,
                output_path=output_path,
                f0method=params.f0method,
                pitch=0,  # Use default pitch
                index_rate=params.index_rate,
                filter_radius=params.filter_radius,
                resample_sr=params.resample_sr,
                rms_mix_rate=params.rms_mix_rate,
                protect=params.protect
            )
            
            # Read converted audio
            with open(output_path, 'rb') as f:
                result_bytes = f.read()
            
            # Encode to base64
            result_base64 = base64.b64encode(result_bytes).decode('utf-8')
            
            logger.info(f"Conversion completed: {len(result_bytes)} bytes")
            
            return {
                "status": "converted",
                "audio_base64": result_base64,
                "model": request.model_name,
                "params_used": params.dict()
            }
            
        finally:
            # Cleanup temp files
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Separate vocals (Demucs)
@app.post("/separate")
async def separate_vocals_endpoint(request: SeparationRequest):
    """
    Separate vocals from audio using Demucs
    
    Args:
        request: Audio data (base64) + model preset
        
    Returns:
        Separated vocals and accompaniment (base64)
    """
    try:
        import os
        import tempfile
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_base64)
        
        logger.info(f"Separating vocals with model: {request.model}")
        
        # Create temp directory for Demucs output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write input audio
            input_path = os.path.join(temp_dir, "input.wav")
            with open(input_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Separate vocals
            vocals_path, accompaniment_path = separate_vocals(input_path, temp_dir)
            
            # Read separated audio files
            with open(vocals_path, 'rb') as f:
                vocals_bytes = f.read()
            
            accompaniment_bytes = None
            if os.path.exists(accompaniment_path):
                with open(accompaniment_path, 'rb') as f:
                    accompaniment_bytes = f.read()
            
            # Encode to base64
            vocals_base64 = base64.b64encode(vocals_bytes).decode('utf-8')
            accompaniment_base64 = None
            if accompaniment_bytes:
                accompaniment_base64 = base64.b64encode(accompaniment_bytes).decode('utf-8')
            
            logger.info(f"Separation completed: vocals={len(vocals_bytes)} bytes")
            
            return {
                "status": "separated",
                "vocals_base64": vocals_base64,
                "accompaniment_base64": accompaniment_base64,
                "model": request.model
            }
            
    except Exception as e:
        logger.error(f"Separation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Set device
@app.post("/set_device")
async def set_device(device: str = "cuda:0"):
    """Set computation device (cuda:0, cpu, etc.)"""
    global rvc_instance
    
    if not RVC_AVAILABLE:
        raise HTTPException(status_code=503, detail="RVC not available")
    
    try:
        import torch
        
        logger.info(f"Setting device to: {device}")
        
        # Validate device
        if device.startswith("cuda"):
            if not torch.cuda.is_available():
                raise HTTPException(status_code=400, detail="CUDA not available")
            
            # Extract device index
            device_id = 0
            if ":" in device:
                device_id = int(device.split(":")[1])
            
            if device_id >= torch.cuda.device_count():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid device ID: {device_id}. Available: 0-{torch.cuda.device_count()-1}"
                )
        
        # Reinitialize RVC with new device
        rvc_instance = RVC(device=device)
        
        # Clear model cache (device changed)
        model_cache.clear()
        torch.cuda.empty_cache()
        
        logger.info(f"Device switched successfully to: {device}")
        
        return {
            "status": "device_set",
            "device": device,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set device: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Main entry point
if __name__ == "__main__":
    logger.info("Starting RVC server on http://0.0.0.0:10102")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=10102,
        reload=True,
        log_level="info"
    )
