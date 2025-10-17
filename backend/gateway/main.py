"""
FastAPI Gateway - Job Management & Progress Tracking
Port: 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import os
import time
from loguru import logger
from typing import Dict, Any

# Import routers
from routers import tts, rvc
from config import config

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("Starting MioVo Gateway...")
    
    # Startup: Validate configuration
    if not config.validate_config():
        logger.warning("Configuration validation failed. Some features may not work properly.")
    
    logger.info(f"Real services enabled: {config.ENABLE_REAL_SERVICES}")
    if config.ENABLE_REAL_SERVICES:
        logger.info(f"AivisSpeech URL: {config.get_aivisspeech_url()}")
        logger.info(f"RVC URL: {config.get_rvc_url()}")
    else:
        logger.info("Running in mock mode. Set ENABLE_REAL_SERVICES=true to connect to real services.")
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down MioVo Gateway...")
    
    # Close HTTP clients
    if tts.aivisspeech_client:
        await tts.aivisspeech_client.aclose()
    if rvc.rvc_client:
        await rvc.rvc_client.aclose()

# Create FastAPI app
app = FastAPI(
    title="MioVo Gateway",
    description="Local Voice Studio - API Gateway",
    version="0.2.0",
    lifespan=lifespan
)

# CORS middleware - Updated to include Cloudflare URLs
allowed_origins = config.ALLOWED_ORIGINS.copy()

# Add Replit domains if available
if replit_domain := os.getenv("REPL_SLUG"):
    replit_origins = [
        f"https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER', '')}.repl.co",
        f"https://{os.getenv('REPL_SLUG')}-{os.getenv('REPL_OWNER', '')}.replit.dev",
    ]
    allowed_origins.extend(replit_origins)

# Add specific Cloudflare tunnel domains if provided
if cloudflare_domain := os.getenv("CLOUDFLARE_DOMAIN"):
    allowed_origins.append(f"https://{cloudflare_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tts.router)
app.include_router(rvc.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "miovo-gateway",
        "version": "0.2.0",
        "mode": "production" if config.ENABLE_REAL_SERVICES else "mock"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "MioVo Gateway",
        "version": "0.2.0",
        "mode": "production" if config.ENABLE_REAL_SERVICES else "mock",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "services_status": "/api/services/status",
            "tts": {
                "synthesize": "/tts/synthesize",
                "synthesize_batch": "/tts/synthesize_batch",
                "speakers": "/tts/speakers",
                "health": "/tts/health",
                "test_connection": "/tts/test_connection"
            },
            "rvc": {
                "convert": "/rvc/convert",
                "separate": "/rvc/separate",
                "models": "/rvc/models",
                "health": "/rvc/health",
                "test_connection": "/rvc/test_connection",
                "gpu_info": "/rvc/gpu_info"
            }
        }
    }

# Service status endpoint
@app.get("/api/services/status")
async def get_services_status():
    """
    Check the status of all connected services
    
    Returns comprehensive status information for AivisSpeech and RVC services
    """
    start_time = time.time()
    
    # Initialize status response
    status_response: Dict[str, Any] = {
        "timestamp": time.time(),
        "mode": "production" if config.ENABLE_REAL_SERVICES else "mock",
        "services": {},
        "overall_status": "unknown",
        "total_response_time_ms": 0
    }
    
    # Check AivisSpeech status
    aivisspeech_status = {
        "available": False,
        "url": config.get_aivisspeech_url(),
        "response_time_ms": None,
        "error": None
    }
    
    try:
        tts_start = time.time()
        
        if config.ENABLE_REAL_SERVICES:
            # Test real connection
            client = await tts.get_aivisspeech_client()
            response = await client.get("/speakers", timeout=5.0)
            
            if response.status_code == 200:
                aivisspeech_status["available"] = True
                speakers = response.json()
                aivisspeech_status["speakers_count"] = len(speakers) if isinstance(speakers, list) else 0
            else:
                aivisspeech_status["error"] = f"Unexpected status: {response.status_code}"
        else:
            # Mock mode
            aivisspeech_status["available"] = True
            aivisspeech_status["speakers_count"] = 3  # Mock speakers
        
        aivisspeech_status["response_time_ms"] = round((time.time() - tts_start) * 1000, 2)
        
    except Exception as e:
        aivisspeech_status["error"] = str(e)
        logger.error(f"Failed to check AivisSpeech status: {e}")
    
    status_response["services"]["aivisspeech"] = aivisspeech_status
    
    # Check RVC status
    rvc_status = {
        "available": False,
        "url": config.get_rvc_url(),
        "response_time_ms": None,
        "error": None,
        "gpu_available": False
    }
    
    try:
        rvc_start = time.time()
        
        if config.ENABLE_REAL_SERVICES:
            # Test real connection
            client = await rvc.get_rvc_client()
            response = await client.get("/health", timeout=5.0)
            
            if response.status_code == 200:
                rvc_status["available"] = True
                health_data = response.json()
                rvc_status["gpu_available"] = health_data.get("gpu_available", False)
                rvc_status["models_loaded"] = health_data.get("models_loaded", 0)
            else:
                rvc_status["error"] = f"Unexpected status: {response.status_code}"
        else:
            # Mock mode
            rvc_status["available"] = True
            rvc_status["gpu_available"] = True
            rvc_status["models_loaded"] = 2  # Mock models
        
        rvc_status["response_time_ms"] = round((time.time() - rvc_start) * 1000, 2)
        
    except Exception as e:
        rvc_status["error"] = str(e)
        logger.error(f"Failed to check RVC status: {e}")
    
    status_response["services"]["rvc"] = rvc_status
    
    # Calculate overall status
    all_available = all([
        aivisspeech_status["available"],
        rvc_status["available"]
    ])
    
    any_available = any([
        aivisspeech_status["available"],
        rvc_status["available"]
    ])
    
    if all_available:
        status_response["overall_status"] = "healthy"
    elif any_available:
        status_response["overall_status"] = "degraded"
    else:
        status_response["overall_status"] = "unhealthy"
    
    # Total response time
    status_response["total_response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Add configuration info
    status_response["configuration"] = {
        "real_services_enabled": config.ENABLE_REAL_SERVICES,
        "service_timeout": config.SERVICE_TIMEOUT,
        "max_audio_length": config.MAX_AUDIO_LENGTH
    }
    
    # Add performance metrics if available
    if config.ENABLE_REAL_SERVICES:
        status_response["performance"] = {
            "expected_tts_speed": "Real-time or faster with RTX 5090",
            "expected_rvc_speed": "2-5x real-time with RTX 5090",
            "gpu_acceleration": rvc_status.get("gpu_available", False)
        }
    
    return status_response

# Configuration endpoint
@app.get("/api/config")
async def get_configuration():
    """Get current configuration (safe to expose)"""
    return {
        "mode": "production" if config.ENABLE_REAL_SERVICES else "mock",
        "services": {
            "aivisspeech": {
                "url": config.get_aivisspeech_url() if config.ENABLE_REAL_SERVICES else "mock://localhost",
                "enabled": config.ENABLE_REAL_SERVICES
            },
            "rvc": {
                "url": config.get_rvc_url() if config.ENABLE_REAL_SERVICES else "mock://localhost",
                "enabled": config.ENABLE_REAL_SERVICES
            }
        },
        "limits": {
            "max_audio_length_seconds": config.MAX_AUDIO_LENGTH,
            "max_text_length": config.MAX_TEXT_LENGTH,
            "max_batch_size": config.MAX_BATCH_SIZE,
            "service_timeout_seconds": config.SERVICE_TIMEOUT
        },
        "audio_settings": {
            "sample_rate": config.DEFAULT_SAMPLE_RATE,
            "channels": config.DEFAULT_CHANNELS,
            "bit_depth": config.DEFAULT_BIT_DEPTH
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Main entry point
if __name__ == "__main__":
    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
