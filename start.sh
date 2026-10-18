#!/bin/bash
# Script de inicio para CineFlow AI
echo "🚀 Iniciando CineFlow AI Studio..."
cd "$(dirname "$0")"

# Verificar ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Configurando enlace a FFmpeg 7.1..."
    export PATH="/usr/local/bin:$PATH"
fi

# Iniciar servidor FastAPI
cd backend
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
