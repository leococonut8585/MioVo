"""
AivisSpeech Engine API Client
VOICEVOX-compatible HTTP API wrapper
"""
from typing import Dict, List, Any, Optional
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class AivisSpeechClient:
    """AivisSpeech Engine API client wrapper"""
    
    def __init__(self, base_url: str = "http://localhost:10101"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.8))
    async def get_speakers(self) -> List[Dict[str, Any]]:
        """
        Get available speakers and styles
        
        Returns:
            List of speakers with styles
        """
        try:
            response = await self.client.get(f"{self.base_url}/speakers")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get speakers: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.8))
    async def audio_query(
        self,
        text: str,
        speaker_id: int,
        core_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create audio query from text
        
        Args:
            text: Text to synthesize
            speaker_id: Speaker style ID
            core_version: Core version (optional, ignored by AivisSpeech)
            
        Returns:
            AudioQuery JSON
        """
        params = {
            "text": text,
            "speaker": speaker_id
        }
        if core_version:
            params["core_version"] = core_version
            
        try:
            response = await self.client.post(
                f"{self.base_url}/audio_query",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create audio query: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.8))
    async def synthesis(
        self,
        audio_query: Dict[str, Any],
        speaker_id: int,
        enable_interrogative_upspeak: bool = True
    ) -> bytes:
        """
        Synthesize speech from audio query
        
        Args:
            audio_query: AudioQuery JSON from audio_query()
            speaker_id: Speaker style ID
            enable_interrogative_upspeak: Enable upspeak (ignored by AivisSpeech)
            
        Returns:
            WAV file bytes
        """
        params = {
            "speaker": speaker_id,
            "enable_interrogative_upspeak": enable_interrogative_upspeak
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/synthesis",
                params=params,
                json=audio_query,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error(f"Failed to synthesize speech: {e}")
            raise
    
    async def tts(
        self,
        text: str,
        speaker_id: int,
        speed_scale: float = 1.0,
        pitch_scale: float = 0.0,
        intonation_scale: float = 1.0,
        volume_scale: float = 1.0
    ) -> bytes:
        """
        Text-to-Speech (simplified API)
        
        Args:
            text: Text to synthesize
            speaker_id: Speaker style ID
            speed_scale: Speech speed (0.5-2.0)
            pitch_scale: Pitch shift (0.0-2.0)
            intonation_scale: Intonation strength (0.0-2.0)
            volume_scale: Volume (0.0-2.0)
            
        Returns:
            WAV file bytes
        """
        # Create audio query
        audio_query = await self.audio_query(text, speaker_id)
        
        # Apply modifications
        audio_query['speedScale'] = speed_scale
        audio_query['pitchScale'] = pitch_scale
        audio_query['intonationScale'] = intonation_scale
        audio_query['volumeScale'] = volume_scale
        
        # Synthesize
        return await self.synthesis(audio_query, speaker_id)
    
    async def health_check(self) -> bool:
        """
        Check if AivisSpeech Engine is running
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/speakers", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
