FROM python:3.12-slim

# Instalar FFmpeg en el sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY . .

# Render, Railway y otros servicios inyectan la variable PORT
ENV PORT=8000
EXPOSE 8000

# Arrancar la aplicación
CMD ["sh", "-c", "python3 backend/app.py"]
