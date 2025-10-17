# MioVo Gateway API Documentation

## Overview
MioVo Gateway is a unified API service that connects to AivisSpeech (TTS) and RVC (Voice Conversion) services via Cloudflare Tunnel.

## Configuration

### Environment Variables
- `ENABLE_REAL_SERVICES`: Set to `true` to enable real service connections (default: `false`)
- `AIVISSPEECH_URL`: URL for AivisSpeech service via Cloudflare Tunnel
- `RVC_URL`: URL for RVC service via Cloudflare Tunnel
- `SERVICE_TIMEOUT`: Request timeout in seconds (default: 30)
- `MAX_AUDIO_LENGTH`: Maximum audio length in seconds (default: 300)

### Running the Service
```bash
cd backend/gateway
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Core Endpoints

#### GET /
Root endpoint with API information
- Returns: Service information and available endpoints

#### GET /health
Health check endpoint
- Returns: Service status and mode (production/mock)

#### GET /api/services/status
Comprehensive status of all connected services
- Returns: Detailed status of AivisSpeech and RVC services
- Includes response times, availability, and configuration

#### GET /api/config
Current configuration (safe to expose)
- Returns: Service settings, limits, and audio configuration

### TTS (Text-to-Speech) Endpoints

#### POST /tts/synthesize
Synthesize speech from text
- Request Body:
```json
{
  "text": "Hello World",
  "speaker_id": 0,
  "speed_scale": 1.0,
  "pitch_scale": 0.0,
  "intonation_scale": 1.0,
  "volume_scale": 1.0
}
```
- Returns: TaskResponse with audio_base64

#### POST /tts/synthesize_batch
Batch synthesis for multiple texts
- Request Body:
```json
{
  "texts": ["Text 1", "Text 2"],
  "speaker_id": 0,
  "speed_scale": 1.0,
  "pitch_scale": 0.0,
  "intonation_scale": 1.0,
  "volume_scale": 1.0
}
```
- Returns: Concatenated WAV audio stream

#### GET /tts/speakers
Get available speakers/styles
- Returns: List of available speakers

#### GET /tts/health
Check AivisSpeech Engine health
- Returns: Service health status

#### GET /tts/test_connection
Test connection to AivisSpeech service
- Returns: Connection status and details

### RVC (Voice Conversion) Endpoints

#### POST /rvc/convert
Convert voice using RVC
- Request Body:
```json
{
  "audio_base64": "base64_encoded_audio",
  "model_name": "model_name",
  "f0method": "rmvpe",
  "protect": 0.5,
  "index_rate": 0.75,
  "filter_radius": 3
}
```
- Returns: TaskResponse with converted audio

#### POST /rvc/separate
Separate vocals from audio
- Request Body:
```json
{
  "audio_base64": "base64_encoded_audio",
  "model": "htdemucs",
  "shifts": 1,
  "overlap": 0.25
}
```
- Returns: TaskResponse with vocals and instrumental tracks

#### GET /rvc/models
Get available RVC models
- Returns: List of available models

#### POST /rvc/models/{model_name}/load
Load RVC model into memory
- Returns: Model loading status

#### GET /rvc/health
Check RVC service health
- Returns: Service health status

#### GET /rvc/test_connection
Test connection to RVC service
- Returns: Connection status and GPU information

#### GET /rvc/gpu_info
Get GPU information from RVC service
- Returns: GPU availability and specifications

## Response Models

### TaskResponse
```json
{
  "task_id": "uuid",
  "type": "tts|rvc|separation",
  "status": "completed|failed",
  "progress": 100.0,
  "result": {
    "audio_base64": "base64_data",
    "additional_info": "..."
  },
  "error": null,
  "created_at": "2025-10-17T05:00:00",
  "updated_at": "2025-10-17T05:00:01"
}
```

## Mock Mode
When `ENABLE_REAL_SERVICES=false`, the service runs in mock mode:
- Returns simulated responses for testing
- No actual connection to AivisSpeech or RVC services
- Useful for development and testing

## Production Mode
When `ENABLE_REAL_SERVICES=true`:
- Connects to real services via Cloudflare Tunnel
- Uses URLs specified in environment variables
- Full GPU acceleration support (RTX 5090)
- Real-time or faster processing

## Performance
With Intel Core Ultra 9 285K + RTX 5090:
- TTS: Real-time or faster synthesis
- RVC: 2-5x real-time voice conversion
- Vocal Separation: Fast processing with GPU acceleration

## CORS Configuration
The service automatically allows:
- Local development (localhost:5000, localhost:5173)
- Replit domains (*.repl.co, *.replit.dev)
- Cloudflare tunnel domains (*.trycloudflare.com)
- Custom domains via CLOUDFLARE_DOMAIN environment variable

## Error Handling
- Comprehensive error responses with status codes
- Detailed logging via loguru
- Fallback to mock mode when services unavailable
- Timeout protection (configurable)