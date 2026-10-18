"""
Motor Especializado de Animación Anime Cinemático (CineAnime Studio).
Enfocado exclusivamente en el estilo visual Seinen/Drama de la imagen de referencia:
1. Animación Cinemática Viva: Movimiento de cámara (Ken Burns), oscilación de luz ambiental cálida,
   partículas de polvo en el haz de luz y grano analógico 35mm.
2. Animador de Secuencias Consecutivas: Conexión de fotogramas continuos con control de FPS,
   modos de bucle (loop / ping-pong) e interpolación de cuadros por FFmpeg.
"""

import os
import math
import random
import subprocess
from typing import List, Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageDraw
import numpy as np

class AnimeAnimator:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render_cinematic_animation(
        self,
        image_path: str,
        output_prefix: str,
        duration: float = 4.0,
        fps: int = 24,
        camera_intensity: float = 0.04,
        enable_light_flicker: bool = True,
        enable_particles: bool = True,
        enable_film_grain: bool = True
    ) -> Dict[str, Any]:
        """
        Anima una imagen estática con la atmósfera viva del estilo anime de referencia:
        - Haz de luz de bombilla oscilante
        - Partículas suspendidas en el haz luminoso
        - Paneo y zoom sutil
        - Textura de película anime 35mm
        """
        img = Image.open(image_path).convert("RGB")
        w, h = img.size
        # Asegurar dimensiones pares para h264
        if w % 2 != 0: w -= 1
        if h % 2 != 0: h -= 1
        img = img.resize((w, h), Image.Resampling.LANCZOS)

        total_frames = int(duration * fps)
        out_mp4 = os.path.join(self.output_dir, f"{output_prefix}.mp4")
        out_gif = os.path.join(self.output_dir, f"{output_prefix}.gif")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{w}x{h}",
            "-pix_fmt", "rgb24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            out_mp4
        ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

        # Partículas suspendidas en el haz de la lámpara
        random.seed(1337)
        particles = [
            {
                "x": random.uniform(w * 0.28, w * 0.72),
                "y": random.uniform(20, h * 0.85),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(0.3, 0.9),
                "r": random.uniform(1.2, 2.8),
                "alpha": random.uniform(0.35, 0.75)
            }
            for _ in range(50)
        ]

        for frame_idx in range(total_frames):
            t = frame_idx / float(fps)
            
            # 1. Movimiento de cámara suave (Ken Burns) con ciclo continuo para loop perfecto
            loop_factor = 0.5 - 0.5 * math.cos(2 * math.pi * t / duration)
            zoom = 1.0 + (camera_intensity * loop_factor)
            
            zw, zh = int(w / zoom), int(h / zoom)
            zx = (w - zw) // 2
            zy = (h - zh) // 2
            
            # Recorte y escalado
            frame_pil = img.crop((zx, zy, zx + zw, zy + zh)).resize((w, h), Image.Resampling.BILINEAR)

            # 2. Oscilación de luz ambiental cálida (bombilla de techo)
            if enable_light_flicker:
                flicker = 1.0 + 0.035 * math.sin(t * 4.5) + 0.015 * math.sin(t * 11.2)
                enh = ImageEnhance.Brightness(frame_pil)
                frame_pil = enh.enhance(flicker)
            else:
                flicker = 1.0

            # 3. Partículas flotantes de polvo en el haz de luz
            if enable_particles:
                draw = ImageDraw.Draw(frame_pil, "RGBA")
                for p in particles:
                    px = (p["x"] + t * p["vx"] * 18) % (w * 0.5) + (w * 0.26)
                    py = (p["y"] + t * p["vy"] * 24) % (h * 0.85) + 20
                    alpha = int(p["alpha"] * 190 * flicker)
                    draw.ellipse([px - p["r"], py - p["r"], px + p["r"], py + p["r"]], fill=(255, 240, 205, alpha))

            # 4. Grano de película anime 35mm
            if enable_film_grain:
                frame_arr = np.array(frame_pil, dtype=np.int16)
                noise = np.random.randint(-5, 6, (h, w, 3), dtype=np.int16)
                frame_arr = np.clip(frame_arr + noise, 0, 255).astype(np.uint8)
                proc.stdin.write(frame_arr.tobytes())
            else:
                proc.stdin.write(frame_pil.tobytes())

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError(f"Error generando MP4: código {proc.returncode}")

        # Generar GIF animado con paleta optimizada
        gif_scale = min(640, w)
        gif_cmd = [
            "ffmpeg", "-y",
            "-i", out_mp4,
            "-vf", f"fps=12,scale={gif_scale}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse",
            out_gif
        ]
        subprocess.run(gif_cmd, capture_output=True)

        size_mp4_mb = round(os.path.getsize(out_mp4) / (1024 * 1024), 2)
        size_gif_mb = round(os.path.getsize(out_gif) / (1024 * 1024), 2) if os.path.exists(out_gif) else 0

        return {
            "success": True,
            "mp4_file": os.path.basename(out_mp4),
            "gif_file": os.path.basename(out_gif),
            "mp4_url": f"/api/video/{os.path.basename(out_mp4)}",
            "gif_url": f"/api/video/{os.path.basename(out_gif)}",
            "duration": duration,
            "fps": fps,
            "total_frames": total_frames,
            "width": w,
            "height": h,
            "size_mp4_mb": size_mp4_mb,
            "size_gif_mb": size_gif_mb
        }

    def render_consecutive_sequence(
        self,
        image_paths: List[str],
        output_prefix: str,
        fps: int = 12,
        loop_mode: str = "loop", # "loop" o "ping_pong"
        interpolation: str = "none" # "none" o "blend"
    ) -> Dict[str, Any]:
        """
        Une varias imágenes consecutivas en una animación fluida:
        - Control exacto de FPS (6, 8, 12, 16, 24)
        - Modo bucle continuo o ida y vuelta (ping-pong)
        - Interpolación opcional entre fotogramas consecutivos
        """
        if not image_paths or len(image_paths) < 2:
            raise ValueError("Se requieren al menos 2 imágenes consecutivas para animar.")

        # Leer primera imagen para dimensiones base
        ref = Image.open(image_paths[0])
        w, h = ref.size
        if w % 2 != 0: w -= 1
        if h % 2 != 0: h -= 1

        # Construir la lista final de fotogramas según el modo
        frames_list = list(image_paths)
        if loop_mode == "ping_pong":
            # Añadir reversa excluyendo los extremos
            frames_list += list(reversed(image_paths[1:-1]))

        # Normalizar todas las imágenes al mismo tamaño en carpeta temporal
        temp_dir = os.path.join(self.output_dir, f"temp_{output_prefix}")
        os.makedirs(temp_dir, exist_ok=True)

        normalized_paths = []
        for i, p in enumerate(frames_list):
            im = Image.open(p).convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
            norm_p = os.path.join(temp_dir, f"frame_{i:04d}.png")
            im.save(norm_p)
            normalized_paths.append(norm_p)

        out_mp4 = os.path.join(self.output_dir, f"{output_prefix}.mp4")
        out_gif = os.path.join(self.output_dir, f"{output_prefix}.gif")

        # Archivo de lista para demuxer concat de FFmpeg
        concat_txt = os.path.join(temp_dir, "concat.txt")
        frame_duration = 1.0 / fps
        with open(concat_txt, "w", encoding="utf-8") as f:
            # Repetir la secuencia 3 veces para que el video tenga al menos un par de segundos
            repeat_count = max(1, int(math.ceil(3.0 / (len(normalized_paths) * frame_duration))))
            for _ in range(repeat_count):
                for p in normalized_paths:
                    f.write(f"file '{os.path.abspath(p)}'\n")
                    f.write(f"duration {frame_duration:.4f}\n")
            # Último frame requiere una línea extra en concat demuxer
            f.write(f"file '{os.path.abspath(normalized_paths[-1])}'\n")

        # Filtro de video
        if interpolation == "blend":
            vf = "tblend=all_mode=average,fps=24"
        else:
            vf = f"fps={fps}"

        cmd_mp4 = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt,
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            out_mp4
        ]
        res = subprocess.run(cmd_mp4, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Error ensamblando secuencia: {res.stderr}")

        # Generar GIF animado
        cmd_gif = [
            "ffmpeg", "-y",
            "-i", out_mp4,
            "-vf", f"fps={fps},scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse",
            out_gif
        ]
        subprocess.run(cmd_gif, capture_output=True)

        # Limpiar temporales
        for p in normalized_paths:
            try: os.remove(p)
            except OSError: pass
        try:
            os.remove(concat_txt)
            os.rmdir(temp_dir)
        except OSError:
            pass

        total_duration = round(len(frames_list) * frame_duration, 2)
        size_mp4_mb = round(os.path.getsize(out_mp4) / (1024 * 1024), 2)
        size_gif_mb = round(os.path.getsize(out_gif) / (1024 * 1024), 2) if os.path.exists(out_gif) else 0

        return {
            "success": True,
            "mp4_file": os.path.basename(out_mp4),
            "gif_file": os.path.basename(out_gif),
            "mp4_url": f"/api/video/{os.path.basename(out_mp4)}",
            "gif_url": f"/api/video/{os.path.basename(out_gif)}",
            "duration": total_duration,
            "fps": fps,
            "frame_count": len(frames_list),
            "width": w,
            "height": h,
            "size_mp4_mb": size_mp4_mb,
            "size_gif_mb": size_gif_mb
        }
