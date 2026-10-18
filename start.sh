#!/bin/bash
# Script de inicio universal para CineAnime Studio
echo "🚀 Iniciando CineAnime Studio..."
cd "$(dirname "$0")"

# 1. Instalar dependencias automáticamente si faltan
if ! python3 -c "import fastapi, uvicorn, PIL, numpy, imageio_ffmpeg" &> /dev/null; then
    echo "📦 Instalando librerías requeridas (requirements.txt)..."
    pip install -r requirements.txt || python3 -m pip install -r requirements.txt
fi

# 2. Configurar FFmpeg automáticamente usando imageio-ffmpeg si no está en el PATH
if ! command -v ffmpeg &> /dev/null; then
    FFMPEG_BIN=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())" 2>/dev/null)
    if [ -n "$FFMPEG_BIN" ]; then
        mkdir -p bin
        ln -sf "$FFMPEG_BIN" bin/ffmpeg
        export PATH="$(pwd)/bin:$PATH"
    fi
fi

# 3. Iniciar servidor FastAPI
cd backend
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
