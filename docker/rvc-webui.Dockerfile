# RVC WebUI Dockerfile
# RVC学習環境（Gradio WebUI）

FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

# 作業ディレクトリ
WORKDIR /workspace

# システム依存関係
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    ffmpeg \
    libsndfile1 \
    build-essential \
    python3-dev \
    aria2 && \
    rm -rf /var/lib/apt/lists/*

# Python 3.10環境作成（fairseq/hydra-core互換のため）
RUN conda create -n py310 python=3.10 -y

# PATH更新
ENV PATH="/opt/conda/envs/py310/bin:$PATH"

# PyTorch 2.7.0 + CUDA 12.8再インストール（conda環境内）
RUN /opt/conda/envs/py310/bin/pip install --no-cache-dir \
    torch==2.7.0+cu128 \
    torchaudio==2.7.0+cu128 \
    --extra-index-url https://download.pytorch.org/whl/cu128

# pip 24.0ダウングレード（omegaconf 2.0.6互換）
RUN /opt/conda/envs/py310/bin/pip install 'pip==24.0'

# RVC WebUI本体
RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git /workspace/RVC-WebUI && \
    cd /workspace/RVC-WebUI && \
    /opt/conda/envs/py310/bin/pip install --no-cache-dir -r requirements.txt

# 事前学習モデルダウンロード
WORKDIR /workspace/RVC-WebUI
RUN mkdir -p assets/pretrained_v2 && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o D32k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/D32k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o D40k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/D40k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o D48k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/D48k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o G32k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/G32k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o G40k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/G40k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o G48k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/G48k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o f0D32k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0D32k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o f0D40k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0D40k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o f0D48k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0D48k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o f0G32k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0G32k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o f0G40k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0G40k.pth && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/pretrained_v2 -o f0G48k.pth \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0G48k.pth

# HuBERT特徴抽出モデル
RUN mkdir -p assets/hubert && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/hubert -o hubert_base.pt \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt

# RMVPEモデル（最新ピッチ抽出）
RUN mkdir -p assets/rmvpe && \
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M \
    -d assets/rmvpe -o rmvpe.pt \
    https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt

# ポート公開
EXPOSE 7865

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7865 || exit 1

# 起動コマンド（Gradio WebUI - listenなしでポートのみ指定）
CMD ["/opt/conda/envs/py310/bin/python", "infer-web.py", "--port", "7865", "--noautoopen"]
