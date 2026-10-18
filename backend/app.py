"""
Servidor CineAnime Studio - Herramienta de Animación Especializada en Estilo Anime Cinemático.
Soporta:
1. Animación Cinemática de Escena (luz ambiental viva, partículas en haz de luz, movimiento 3D de cámara y grano analógico).
2. Animador de Imágenes Consecutivas (interpolación de fotogramas, control de FPS y bucles).
"""

import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.anime_animator import AnimeAnimator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATIC_DIR = os.path.join(ROOT_DIR, "frontend")
UPLOADS_DIR = os.path.join(ROOT_DIR, "uploads")
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

app = FastAPI(title="CineAnime Studio - Animador Anime Cinemático", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

animator = AnimeAnimator(output_dir=OUTPUTS_DIR)

@app.get("/api/reference_image")
def get_reference_image():
    """Devuelve la imagen de referencia del estilo visual anime seinen."""
    ref_path = os.path.join(ASSETS_DIR, "reference_anime.jpg")
    if not os.path.exists(ref_path):
        raise HTTPException(status_code=404, detail="Imagen de referencia no encontrada.")
    return FileResponse(ref_path, media_type="image/jpeg")

@app.get("/api/sample_sequence")
def get_sample_sequence():
    """Devuelve la lista de 4 fotogramas consecutivos de ejemplo en el estilo anime."""
    seq_dir = os.path.join(ASSETS_DIR, "sample_sequence")
    files = sorted([f for f in os.listdir(seq_dir) if f.endswith(('.jpg', '.png'))])
    frames = [f"/assets/sample_sequence/{f}" for f in files]
    return {
        "count": len(frames),
        "frames": frames
    }

@app.post("/api/animate/cinematic")
async def animate_cinematic(
    image: Optional[UploadFile] = File(None),
    duration: float = Form(4.0),
    fps: int = Form(24),
    camera_intensity: float = Form(0.04),
    enable_light_flicker: bool = Form(True),
    enable_particles: bool = Form(True),
    enable_film_grain: bool = Form(True)
):
    """
    Anima una imagen fija con la atmósfera viva de la escena anime:
    - Haz de luz de bombilla oscilante
    - Partículas de polvo en el haz luminoso
    - Paneo/zoom cinematográfico continuo
    - Textura de película 35mm
    """
    anim_id = str(uuid.uuid4())[:8]

    if image and image.filename:
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        img_path = os.path.join(UPLOADS_DIR, f"input_{anim_id}{ext}")
        content = await image.read()
        with open(img_path, "wb") as f:
            f.write(content)
    else:
        # Usar la imagen de referencia por defecto
        img_path = os.path.join(ASSETS_DIR, "reference_anime.jpg")

    try:
        res = animator.render_cinematic_animation(
            image_path=img_path,
            output_prefix=f"cinematic_{anim_id}",
            duration=duration,
            fps=fps,
            camera_intensity=camera_intensity,
            enable_light_flicker=enable_light_flicker,
            enable_particles=enable_particles,
            enable_film_grain=enable_film_grain
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar animación: {str(e)}")

@app.post("/api/animate/sequence")
async def animate_sequence(
    images: Optional[List[UploadFile]] = File(None),
    use_sample: bool = Form(False),
    fps: int = Form(12),
    loop_mode: str = Form("loop"),
    interpolation: str = Form("none")
):
    """
    Anima una secuencia de imágenes consecutivas con control de FPS e interpolación.
    """
    anim_id = str(uuid.uuid4())[:8]
    image_paths = []

    if use_sample or not images or len(images) == 0:
        seq_dir = os.path.join(ASSETS_DIR, "sample_sequence")
        sample_files = sorted([f for f in os.listdir(seq_dir) if f.endswith(('.jpg', '.png'))])
        image_paths = [os.path.join(seq_dir, f) for f in sample_files]
    else:
        upload_seq_dir = os.path.join(UPLOADS_DIR, f"seq_{anim_id}")
        os.makedirs(upload_seq_dir, exist_ok=True)
        for idx, file in enumerate(images):
            ext = os.path.splitext(file.filename or f"frame_{idx}.jpg")[1] or ".jpg"
            p = os.path.join(upload_seq_dir, f"frame_{idx:03d}{ext}")
            content = await file.read()
            with open(p, "wb") as f:
                f.write(content)
            image_paths.append(p)

    try:
        res = animator.render_consecutive_sequence(
            image_paths=image_paths,
            output_prefix=f"sequence_{anim_id}",
            fps=fps,
            loop_mode=loop_mode,
            interpolation=interpolation
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al animar secuencia: {str(e)}")

@app.get("/api/video/{filename}")
def stream_media(filename: str):
    """Sirve videos MP4 o GIFs generados para reproducción inline."""
    path = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    media_type = "video/mp4" if filename.endswith(".mp4") else "image/gif"
    return FileResponse(path, media_type=media_type)

@app.get("/api/download/{filename}")
def download_media(filename: str):
    """Descarga forzada de MP4 o GIF."""
    path = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    media_type = "application/octet-stream"
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# Servir archivos estáticos del frontend y assets
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
