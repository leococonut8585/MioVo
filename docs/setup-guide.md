# MioVo Development Environment Setup Guide

## Prerequisites

### System Requirements
- **OS**: Windows 10/11 (recommended), macOS, or Linux
- **GPU**: NVIDIA RTX series (RTX 5090 recommended)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB free space (for models)

### Required Software

#### Windows
- **Node.js**: 18.0.0 or higher
  - Download: https://nodejs.org/
- **Python**: 3.9-3.11
  - Download: https://www.python.org/downloads/
- **NVIDIA Driver**: R570.65 or higher
  - Download: https://www.nvidia.com/download/index.aspx
- **CUDA Toolkit**: 12.8.1
  - Download: https://developer.nvidia.com/cuda-downloads
- **Docker Desktop** (for RVC):
  - Download: https://www.docker.com/products/docker-desktop
  - Enable WSL 2 backend
  - Enable GPU support

#### macOS / Linux
- **Node.js**: 18.0.0 or higher
- **Python**: 3.9-3.11
- **Docker** (for RVC)
- **NVIDIA Container Toolkit** (Linux only)

---

## Step 1: Clone or Initialize Project

```powershell
# Navigate to project directory
cd "C:\Program Files (x86)\APP\MioVo"

# Verify directory structure
ls
```

---

## Step 2: Install Node.js Dependencies

```powershell
# Install frontend dependencies
npm install

# Verify installation
npm list
```

**Expected output**: All dependencies installed without errors.

---

## Step 3: Install Python Dependencies

### 3.1 Create Virtual Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Or activate (macOS/Linux)
source .venv/bin/activate
```

### 3.2 Install Python Packages

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

---

## Step 4: Setup AivisSpeech Engine

### 4.1 Download AivisSpeech Engine

**Option A: Docker (Recommended)**
```powershell
# Pull GPU-enabled Docker image
docker pull ghcr.io/aivis-project/aivisspeech-engine:nvidia-latest

# Run AivisSpeech Engine
docker run --rm --gpus all -p 10101:10101 `
  -v ~/.local/share/AivisSpeech-Engine:/home/user/.local/share/AivisSpeech-Engine-Dev `
  ghcr.io/aivis-project/aivisspeech-engine:nvidia-latest
```

**Option B: Manual Installation**
1. Visit: https://github.com/Aivis-Project/AivisSpeech-Engine/releases
2. Download latest release for Windows
3. Extract to `C:\Program Files\AivisSpeech`
4. Run `AivisSpeech-Engine.exe`

### 4.2 Verify AivisSpeech

```powershell
# Test API
curl http://localhost:10101/speakers

# Or open in browser
start http://localhost:10101/docs
```

**Expected**: Swagger UI opens showing API documentation.

---

## Step 5: Setup RVC Environment (Docker)

### 5.1 Verify Docker GPU Support

```powershell
# Test GPU in Docker
docker run --rm --gpus all nvcr.io/nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi
```

**Expected**: GPU information displayed (e.g., RTX 5090).

### 5.2 Build RVC Container

```powershell
# Navigate to docker directory
cd ../docker

# Build RVC image (this may take 10-20 minutes)
docker-compose build rvc

# Or build with no cache
docker-compose build --no-cache rvc
```

### 5.3 Start RVC Service

```powershell
# Start RVC container
docker-compose up -d rvc

# Check logs
docker-compose logs -f rvc

# Verify health
curl http://localhost:10102/health
```

**Expected**: `{"status": "healthy"}` or similar response.

---

## Step 6: Configure Application

### 6.1 Create Configuration File

```powershell
# Copy template
cp config/default.yml.template config/default.yml

# Or create from scratch
New-Item -Path config/default.yml -ItemType File
```

### 6.2 Edit Configuration

```yaml
# config/default.yml
system:
  cuda_device: "cuda:0"
  model_cache_size: 6
  max_vram_gb: 28

aivisspeech:
  port: 10101
  gpu_mode: true
  chunk_chars: 500
  default_style_id: 888753760

rvc:
  port: 10102
  device: "cuda:0"
  model_dir: "./models/rvc"
  f0method_reading: "rmvpe"
  f0method_singing: "harvest"
  protect: 0.5

processing:
  parallel_tts_chunks: 4
  samplerate: 48000
  bitdepth: 24
```

---

## Step 7: Run Development Servers

### 7.1 Terminal 1: AivisSpeech Engine

```powershell
# If using Docker
docker start aivisspeech-container

# If using standalone
cd "C:\Program Files\AivisSpeech"
.\AivisSpeech-Engine.exe
```

### 7.2 Terminal 2: RVC Service

```powershell
cd docker
docker-compose up rvc
```

### 7.3 Terminal 3: FastAPI Gateway

```powershell
cd backend/gateway
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7.4 Terminal 4: Electron App

```powershell
cd ../../
npm run electron:dev
```

---

## Step 8: Verify Installation

### 8.1 Check All Services

```powershell
# AivisSpeech (should return speaker list)
curl http://localhost:10101/speakers

# RVC (should return health status)
curl http://localhost:10102/health

# Gateway (should return API info)
curl http://localhost:8000/

# Electron (app window should open)
```

### 8.2 Test Basic Flow

1. Open MioVo application
2. Navigate to "朗読モード"
3. Enter test text: "こんにちは、MioVoです。"
4. Click "生成"
5. Verify audio plays correctly

---

## Troubleshooting

### Issue: Docker GPU Not Detected

**Solution**:
```powershell
# Update NVIDIA Container Toolkit
wsl --update
docker run --rm --gpus all nvcr.io/nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi

# If still failing, reinstall Docker Desktop with GPU support enabled
```

### Issue: AivisSpeech Port Conflict

**Solution**:
```powershell
# Find process using port 10101
netstat -ano | findstr :10101

# Kill process (replace PID)
taskkill /F /PID <PID>

# Or change port in config
```

### Issue: Python Virtual Environment Not Activating

**Solution**:
```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then reactivate
.\.venv\Scripts\Activate.ps1
```

### Issue: RVC Container Build Fails

**Solution**:
```powershell
# Check Docker memory settings (increase to 8GB+)
# Check disk space (need 20GB+ free)
# Try building with verbose output
docker-compose build --no-cache --progress=plain rvc
```

### Issue: CUDA Version Mismatch

**Solution**:
```powershell
# Verify CUDA version
nvcc --version

# Verify Driver version
nvidia-smi

# If mismatch, update driver to R570.65+
```

---

## Next Steps

After successful setup:

1. **Read Documentation**
   - API Reference: `docs/api-reference.md`
   - Architecture: `docs/project-structure.md`
   - Decisions: `docs/decisions.md`

2. **Download Models**
   ```powershell
   python scripts/download-models.py
   ```

3. **Run Tests**
   ```powershell
   npm test
   cd backend && pytest
   ```

4. **Start Development**
   - Frontend: Edit files in `src/`
   - Backend: Edit files in `backend/`
   - Hot reload enabled for both

---

## Additional Resources

- **AivisSpeech**: https://aivis-project.com/
- **RVC Python**: https://github.com/litagin02/rvc-python
- **Docker GPU**: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/
- **Electron**: https://www.electronjs.org/docs

---

## Quick Start Script (Windows)

Save as `setup.ps1` and run:

```powershell
# setup.ps1 - MioVo Quick Setup
$ErrorActionPreference = "Stop"

Write-Host "MioVo Setup Starting..." -ForegroundColor Cyan

# 1. Install Node dependencies
Write-Host "[1/5] Installing Node dependencies..." -ForegroundColor Yellow
npm install

# 2. Setup Python environment
Write-Host "[2/5] Setting up Python environment..." -ForegroundColor Yellow
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# 3. Build Docker images
Write-Host "[3/5] Building Docker images..." -ForegroundColor Yellow
cd docker
docker-compose build

# 4. Start services
Write-Host "[4/5] Starting services..." -ForegroundColor Yellow
docker-compose up -d

# 5. Wait for services
Write-Host "[5/5] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verify
Write-Host "`nVerifying services..." -ForegroundColor Cyan
curl http://localhost:10102/health

Write-Host "`nSetup Complete!" -ForegroundColor Green
Write-Host "Run 'npm run electron:dev' to start the app" -ForegroundColor Cyan
```

---

## Support

For issues or questions:
1. Check `docs/sources.md` for reference materials
2. Review `memory-bank/progress.md` for known issues
3. Create an issue in the project repository
