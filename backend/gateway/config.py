"""
Configuration for MioVo Gateway
Manages service URLs and settings
"""

import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Service URLs - can be overridden by environment variables
    AIVISSPEECH_URL: str = os.getenv('AIVISSPEECH_URL', 'http://localhost:10101')
    RVC_URL: str = os.getenv('RVC_URL', 'http://localhost:10102')
    
    # Service settings
    ENABLE_REAL_SERVICES: bool = os.getenv('ENABLE_REAL_SERVICES', 'false').lower() == 'true'
    SERVICE_TIMEOUT: int = int(os.getenv('SERVICE_TIMEOUT', '30'))
    MAX_AUDIO_LENGTH: int = int(os.getenv('MAX_AUDIO_LENGTH', '300'))  # seconds
    
    # CORS settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5173",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5173",
        "https://*.repl.co",
        "https://*.replit.dev",
        "https://*.replit.app",
        # Cloudflare tunnel domains
        "https://*.trycloudflare.com"
    ]
    
    # Audio settings
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_CHANNELS = 1
    DEFAULT_BIT_DEPTH = 16
    
    # Processing settings
    MAX_TEXT_LENGTH = 5000
    MAX_BATCH_SIZE = 10
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.ENABLE_REAL_SERVICES
    
    @classmethod
    def get_aivisspeech_url(cls) -> str:
        """Get AivisSpeech service URL"""
        return cls.AIVISSPEECH_URL
    
    @classmethod
    def get_rvc_url(cls) -> str:
        """Get RVC service URL"""
        return cls.RVC_URL
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        if cls.ENABLE_REAL_SERVICES:
            if not cls.AIVISSPEECH_URL or not cls.RVC_URL:
                print("⚠️ Real services enabled but URLs not configured")
                return False
            
            # Check if URLs are valid
            for url in [cls.AIVISSPEECH_URL, cls.RVC_URL]:
                if not url.startswith(('http://', 'https://')):
                    print(f"⚠️ Invalid URL format: {url}")
                    return False
        
        return True

# Create config instance
config = Config()