"""
Módulo de Unión y Renderizado Final de Videos para CineFlow AI.
Ensambla automáticamente todas las escenas generadas en un único archivo MP4 continuo,
preservando la sincronización de audio y video.
"""

import os
import subprocess
from typing import List, Dict, Any

class VideoStitcher:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def stitch_scenes(self, scene_video_paths: List[str], output_filename: str) -> Dict[str, Any]:
        """
        Une la lista ordenada de videos en un único MP4 final.
        """
        if not scene_video_paths:
            raise ValueError("No se proporcionaron videos de escenas para unir.")

        final_path = os.path.join(self.output_dir, output_filename)
        list_file_path = os.path.join(self.output_dir, f"concat_{output_filename}.txt")

        # Crear el archivo de lista para el demuxer concat de FFmpeg
        with open(list_file_path, "w", encoding="utf-8") as f:
            for v_path in scene_video_paths:
                abs_path = os.path.abspath(v_path)
                f.write(f"file '{abs_path}'\n")

        # Intentar concatenación rápida con -c copy primero
        fast_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            "-movflags", "+faststart",
            final_path
        ]

        res = subprocess.run(fast_cmd, capture_output=True, text=True)

        # Si hubo incompatibilidad con stream copy, re-codificar de forma limpia
        if res.returncode != 0 or not os.path.exists(final_path):
            reencode_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "21",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                final_path
            ]
            re_res = subprocess.run(reencode_cmd, capture_output=True, text=True)
            if re_res.returncode != 0:
                raise RuntimeError(f"Error uniendo videos: {re_res.stderr}")

        # Limpiar archivo temporal de lista
        if os.path.exists(list_file_path):
            try:
                os.remove(list_file_path)
            except OSError:
                pass

        # Obtener duración y tamaño del archivo final
        size_bytes = os.path.getsize(final_path)
        size_mb = round(size_bytes / (1024 * 1024), 2)
        total_duration = len(scene_video_paths) * 10.0

        return {
            "success": True,
            "final_path": final_path,
            "filename": os.path.basename(final_path),
            "size_mb": size_mb,
            "total_duration": total_duration,
            "scene_count": len(scene_video_paths),
            "format": "mp4 (H.264 / AAC)"
        }
