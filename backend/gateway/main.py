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
from loguru import logger

# Import routers
from routers import tts, rvc

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("Starting MioVo Gateway...")
    
    # Startup: Initialize services
    # TODO: Check AivisSpeech health
    # TODO: Check RVC health
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down MioVo Gateway...")

# Create FastAPI app
app = FastAPI(
    title="MioVo Gateway",
    description="Local Voice Studio - API Gateway",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
allowed_origins = [
    "http://localhost:5000",
    "https://localhost:5000",
]
# Add Replit domains if available
if replit_domain := os.getenv("REPL_SLUG"):
    allowed_origins.extend([
        f"https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER', '')}.repl.co",
        f"https://{os.getenv('REPL_SLUG')}-{os.getenv('REPL_OWNER', '')}.replit.dev",
    ])

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
        "version": "0.1.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "MioVo Gateway",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
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
