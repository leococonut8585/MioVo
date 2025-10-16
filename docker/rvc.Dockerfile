# RVC Service Dockerfile
# Base: PyTorch official container with RTX 5090 (SM_120) support
# Strategy A: PyTorch 2.7.0 + CUDA 12.8 + Python 3.10 (計画書・検証結果に基づく)

FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

LABEL maintainer="MioVo Project"
LABEL description="RVC Voice Conversion Service with RTX 5090 support (Python 3.10)"

# Set working directory
WORKDIR /app

# Create conda environment with Python 3.10
# (Base image has Python 3.11 which causes fairseq/hydra-core dataclass issues)
RUN conda create -n py310 python=3.10 -y && \
    conda clean -ya

# Install PyTorch 2.7.0 with CUDA 12.8 in Python 3.10 environment
RUN /opt/conda/envs/py310/bin/pip install --no-cache-dir \
    torch==2.7.0+cu128 \
    torchaudio==2.7.0+cu128 \
    --index-url https://download.pytorch.org/whl/cu128

# Update PATH to use Python 3.10 environment by default
ENV PATH="/opt/conda/envs/py310/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy RVC requirements
COPY backend/rvc/requirements.txt /app/requirements.txt

# Install Python dependencies
# Note: PyTorch is already provided by base image
RUN pip install --no-cache-dir -r requirements.txt

# Downgrade pip to 24.0 to allow omegaconf 2.0.6 installation
# (rvc-python requires omegaconf==2.0.6 which has legacy metadata format)
# See: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/issues/2244
RUN /opt/conda/envs/py310/bin/pip install --no-cache-dir 'pip==24.0'

# Install rvc-python from PyPI (official package)
# Python 3.10 resolves dataclass mutable default issues in fairseq/hydra-core
RUN /opt/conda/envs/py310/bin/pip install --no-cache-dir rvc-python

# Copy RVC service code
COPY backend/rvc /app

# Create model directory
RUN mkdir -p /models

# Expose RVC API port
EXPOSE 10102

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:10102/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV RVC_PORT=10102
ENV RVC_MODEL_DIR=/models

# Run RVC API server
CMD ["python", "server.py"]
