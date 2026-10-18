"""
Motor de Animación Procedural y Renderizado de Escenas para CineFlow AI.
Genera secuencias animadas de 10 segundos (300 fotogramas a 30fps)
manteniendo la coherencia de personajes, escenarios y el estilo visual seleccionado.
"""

import math
import subprocess
import os
import random
from typing import Dict, Any, Callable, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class SceneAnimator:
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self._font_title = self._load_font(28, bold=True)
        self._font_sub = self._load_font(20, bold=False)
        self._font_badge = self._load_font(16, bold=True)

    def _load_font(self, size: int, bold: bool = False):
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf"
        ]
        for p in font_paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def render_scene_video(
        self,
        scene: Dict[str, Any],
        audio_file: str,
        output_file: str,
        duration: float = 10.0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> str:
        """
        Renderiza la escena completa de 10 segundos y la combina con el audio sincronizado.
        """
        total_frames = int(duration * self.fps)
        coherence = scene.get("coherence", {})
        style_id = coherence.get("style_id", "ghibli")
        palette = coherence.get("palette", {})
        protagonist = coherence.get("protagonist", {})
        narration = scene.get("narration", "")
        title = scene.get("title", f"Escena {scene.get('scene_number', 1)}")
        scene_num = scene.get("scene_number", 1)

        # Preparar partículas aleatorias pero coherentes usando una semilla fija por escena
        random.seed(42 + scene_num * 101)
        particles = [
            {
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "vx": random.uniform(-1.5, 2.5),
                "vy": random.uniform(-0.5, 1.8),
                "size": random.randint(3, 8),
                "alpha": random.randint(120, 220)
            }
            for _ in range(35)
        ]

        # Comando de FFmpeg para recibir rawvideo en RGB24 y combinarlo con el audio
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24",
            "-r", str(self.fps),
            "-i", "-",  # Video desde stdin
            "-i", audio_file,  # Pista de audio sintetizada / clonada
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration),
            "-shortest",
            output_file
        ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

        for frame_idx in range(total_frames):
            t = frame_idx / float(self.fps)
            frame_img = self._generate_frame(
                t=t,
                frame_idx=frame_idx,
                total_frames=total_frames,
                style_id=style_id,
                palette=palette,
                protagonist=protagonist,
                scene_num=scene_num,
                title=title,
                narration=narration,
                particles=particles
            )
            proc.stdin.write(frame_img.tobytes())

            # Reportar progreso cada 30 cuadros (1 segundo)
            if progress_callback and (frame_idx % 30 == 0 or frame_idx == total_frames - 1):
                progress_callback(frame_idx + 1, total_frames, f"Renderizando cuadro {frame_idx + 1}/{total_frames}")

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError(f"Error renderizando video de escena {scene_num}")

        return output_file

    def _generate_frame(
        self,
        t: float,
        frame_idx: int,
        total_frames: int,
        style_id: str,
        palette: Dict[str, Any],
        protagonist: Dict[str, Any],
        scene_num: int,
        title: str,
        narration: str,
        particles: list
    ) -> Image.Image:
        """
        Genera un fotograma individual aplicando la estética, movimiento de cámara,
        animación del personaje y efectos ambientales de la escena.
        """
        w, h = self.width, self.height
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img, "RGBA")

        # 1. Cielo con degradado suave
        sky_top = palette.get("sky_top", (135, 206, 235))
        sky_bottom = palette.get("sky_bottom", (255, 248, 220))
        
        # Efecto de cámara lenta Ken Burns (leve paneo / zoom)
        cam_shift = math.sin(t * 0.25) * 15

        for y in range(h):
            ratio = y / float(h)
            r = int(sky_top[0] * (1 - ratio) + sky_bottom[0] * ratio)
            g = int(sky_top[1] * (1 - ratio) + sky_bottom[1] * ratio)
            b = int(sky_top[2] * (1 - ratio) + sky_bottom[2] * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # 2. Sol o Luna ambiental
        sun_color = palette.get("accent", (255, 200, 80))
        sun_x = int(w * 0.78 + cam_shift * 0.3)
        sun_y = int(h * 0.26)
        sun_r = 55
        # Resplandor exterior
        draw.ellipse([sun_x - sun_r - 20, sun_y - sun_r - 20, sun_x + sun_r + 20, sun_y + sun_r + 20], fill=(*sun_color, 45))
        draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(*sun_color, 210))

        # 3. Nubes o Siluetas flotantes de fondo
        cloud_col = palette.get("cloud", (255, 255, 255))
        for i, cx_base in enumerate([0.15, 0.48, 0.85]):
            cx = (cx_base * w + t * (8 + i * 4)) % (w + 200) - 100
            cy = h * (0.18 + i * 0.08)
            # Dibujar nube con arcos superpuestos
            draw.ellipse([cx - 70, cy - 30, cx + 70, cy + 30], fill=(*cloud_col, 160))
            draw.ellipse([cx - 40, cy - 45, cx + 40, cy + 25], fill=(*cloud_col, 190))
            draw.ellipse([cx + 20, cy - 35, cx + 90, cy + 25], fill=(*cloud_col, 150))

        # 4. Colinas distantes (Paralaje capa 1)
        hills_far = palette.get("hills_far", (100, 150, 110))
        far_points = [(0, h)]
        for x in range(0, w + 30, 30):
            yh = h * 0.52 + math.sin((x + t * 5 + cam_shift) * 0.005) * 45 + math.cos(x * 0.01) * 20
            far_points.append((x, yh))
        far_points.append((w, h))
        draw.polygon(far_points, fill=(*hills_far, 240))

        # 5. Colinas cercanas / Estructuras (Paralaje capa 2)
        hills_near = palette.get("hills_near", (50, 120, 70))
        near_points = [(0, h)]
        for x in range(0, w + 25, 25):
            yh = h * 0.64 + math.sin((x + t * 15 + cam_shift * 2) * 0.008) * 35 + math.sin(x * 0.02) * 15
            near_points.append((x, yh))
        near_points.append((w, h))
        draw.polygon(near_points, fill=(*hills_near, 255))

        # 6. Suelo / Plataforma en primer plano
        ground_col = palette.get("ground", (35, 90, 45))
        draw.rectangle([0, int(h * 0.80), w, h], fill=(*ground_col, 255))

        # Si es Cyberpunk, añadir líneas de cuadrícula neón en el suelo
        if style_id == "cyberpunk":
            for gy in range(int(h * 0.80), h, 18):
                draw.line([(0, gy), (w, gy)], fill=(*palette.get("accent", (0, 240, 255)), 90), width=1)
            for gx in range(0, w, 60):
                draw.line([(gx, int(h * 0.80)), (int(w/2 + (gx - w/2) * 1.8), h)], fill=(*palette.get("accent", (0, 240, 255)), 70), width=1)

        # 7. Personaje Principal (Coherente entre escenas)
        char_x = int(w * 0.35 + math.sin(t * 1.2) * 15)
        # Respiración y ligero paso
        breath = math.sin(t * 3.0) * 4
        char_y = int(h * 0.72 + breath)
        self._draw_character(draw, char_x, char_y, protagonist, style_id, t, breath)

        # 8. Efectos Atmosféricos según el estilo
        self._draw_atmosphere(draw, style_id, palette, particles, t, w, h)

        # Si es Pixel Art, aplicar textura de cuadrícula retro
        if style_id == "pixelart":
            self._apply_pixel_effect(draw, w, h)

        # 9. Barra inferior cinematográfica con subtítulos y título
        self._draw_ui_overlay(draw, scene_num, title, narration, style_id, palette, w, h)

        return img

    def _draw_character(
        self,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        protagonist: Dict[str, Any],
        style_id: str,
        t: float,
        breath: float
    ):
        """Dibuja el personaje coherente con animación de extremidades, ojos y boca (lip-sync)."""
        skin = protagonist.get("skin_color", (255, 220, 185))
        clothes = protagonist.get("clothes_color", (70, 110, 160))
        hair = protagonist.get("hair_color", (74, 44, 23))
        accent = protagonist.get("accent_color", (255, 180, 50))

        # Sombra en el suelo
        draw.ellipse([cx - 45, cy + 38, cx + 45, cy + 54], fill=(15, 25, 20, 120))

        # Piernas
        leg_walk = math.sin(t * 4.0) * 8
        draw.rectangle([cx - 22, cy + 10, cx - 8, cy + 45 + int(leg_walk)], fill=(*clothes, 240))
        draw.rectangle([cx + 8, cy + 10, cx + 22, cy + 45 - int(leg_walk)], fill=(*clothes, 240))
        # Zapatos
        draw.rectangle([cx - 26, cy + 42 + int(leg_walk), cx - 6, cy + 48 + int(leg_walk)], fill=(30, 30, 35))
        draw.rectangle([cx + 6, cy + 42 - int(leg_walk), cx + 26, cy + 48 - int(leg_walk)], fill=(30, 30, 35))

        # Torso / Ropa
        draw.rounded_rectangle([cx - 28, cy - 35, cx + 28, cy + 15], radius=8, fill=(*clothes, 255))
        # Cinturón / Detalle de ropa
        draw.rectangle([cx - 28, cy + 3, cx + 28, cy + 10], fill=(*accent, 255))

        # Capa o Bufanda ondeante (dinámica con el viento)
        scarf_wave = math.sin(t * 5.0) * 12
        scarf_poly = [
            (cx - 20, cy - 25),
            (cx - 50 + int(scarf_wave), cy - 10),
            (cx - 75 + int(scarf_wave * 1.5), cy + 15),
            (cx - 55 + int(scarf_wave), cy + 25),
            (cx - 15, cy - 15)
        ]
        draw.polygon(scarf_poly, fill=(*accent, 240))

        # Cabeza
        head_y = cy - 65
        draw.ellipse([cx - 24, head_y - 24, cx + 24, head_y + 24], fill=(*skin, 255))

        # Cabello estilizado coherente
        hair_poly = [
            (cx - 28, head_y - 10),
            (cx - 30, head_y - 30),
            (cx - 10, head_y - 40),
            (cx + 15, head_y - 38),
            (cx + 30, head_y - 25),
            (cx + 26, head_y - 5),
            (cx + 10, head_y - 20),
            (cx - 8, head_y - 18),
            (cx - 22, head_y - 12)
        ]
        draw.polygon(hair_poly, fill=(*hair, 255))

        # Ojos con parpadeo periódico cada ~3.5 segundos
        blink = (int(t * 10) % 35 == 0)
        eye_y = head_y - 3
        if blink:
            draw.line([(cx - 14, eye_y), (cx - 6, eye_y)], fill=(30, 20, 20), width=2)
            draw.line([(cx + 6, eye_y), (cx + 14, eye_y)], fill=(30, 20, 20), width=2)
        else:
            if style_id == "anime":
                # Ojos estilo anime grandes y expresivos
                draw.ellipse([cx - 16, eye_y - 6, cx - 5, eye_y + 6], fill=(255, 255, 255))
                draw.ellipse([cx - 14, eye_y - 5, cx - 7, eye_y + 5], fill=(35, 75, 140))
                draw.ellipse([cx - 11, eye_y - 4, cx - 8, eye_y - 1], fill=(255, 255, 255))

                draw.ellipse([cx + 5, eye_y - 6, cx + 16, eye_y + 6], fill=(255, 255, 255))
                draw.ellipse([cx + 7, eye_y - 5, cx + 14, eye_y + 5], fill=(35, 75, 140))
                draw.ellipse([cx + 8, eye_y - 4, cx + 11, eye_y - 1], fill=(255, 255, 255))
            else:
                draw.ellipse([cx - 14, eye_y - 4, cx - 6, eye_y + 4], fill=(30, 30, 40))
                draw.ellipse([cx + 6, eye_y - 4, cx + 14, eye_y + 4], fill=(30, 30, 40))
                draw.ellipse([cx - 12, eye_y - 3, cx - 9, eye_y], fill=(255, 255, 255))
                draw.ellipse([cx + 8, eye_y - 3, cx + 11, eye_y], fill=(255, 255, 255))

        # Boca con lip-sync (movimiento sincronizado con la voz hablada)
        mouth_y = head_y + 12
        is_speaking = (t < 8.2) # La narración suele abarcar los primeros ~8 segundos
        if is_speaking:
            mouth_open = abs(math.sin(t * 12.0)) * 6
            draw.ellipse([cx - 6, mouth_y - int(mouth_open/2), cx + 6, mouth_y + int(mouth_open/2) + 2], fill=(160, 40, 50))
        else:
            draw.arc([cx - 5, mouth_y - 3, cx + 5, mouth_y + 4], 0, 180, fill=(120, 40, 40), width=2)

    def _draw_atmosphere(
        self,
        draw: ImageDraw.ImageDraw,
        style_id: str,
        palette: Dict[str, Any],
        particles: list,
        t: float,
        w: int,
        h: int
    ):
        """Efectos visuales atmosféricos específicos para cada estilo."""
        part_col = palette.get("particles", (255, 255, 255))

        if style_id == "ghibli":
            # Esporas doradas de diente de león flotando suavemente
            for p in particles:
                px = (p["x"] + t * p["vx"] * 15) % w
                py = (p["y"] + math.sin(t + p["x"]) * 18 - t * 10) % h
                draw.ellipse([px - p["size"], py - p["size"], px + p["size"], py + p["size"]], fill=(*part_col, p["alpha"]))
                # Estela sutil
                draw.line([(px, py), (px - 8, py + 8)], fill=(*part_col, int(p["alpha"] * 0.4)), width=1)

        elif style_id == "anime":
            # Líneas de velocidad dinámicas y chispas
            for i in range(12):
                sx = random.randint(0, w)
                sy = random.randint(0, h // 2)
                draw.line([(sx, sy), (sx + 40, sy + 15)], fill=(*part_col, 160), width=2)

        elif style_id == "cyberpunk":
            # Lluvia digital de neón y destellos
            for p in particles:
                px = (p["x"] + t * 40) % w
                py = (p["y"] + t * 140) % h
                draw.line([(px, py), (px - 4, py + 18)], fill=(*part_col, 200), width=2)
                # Resplandor de neón cian ocasional
                if p["x"] % 7 == 0:
                    draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(0, 240, 255, 180))

        elif style_id == "comic":
            # Puntos halftone de imprenta retro
            for x in range(0, w, 24):
                for y in range(0, int(h * 0.4), 24):
                    draw.ellipse([x, y, x + 2, y + 2], fill=(20, 20, 30, 45))

    def _apply_pixel_effect(self, draw: ImageDraw.ImageDraw, w: int, h: int):
        """Añade líneas de escaneo retro de monitor CRT / Arcade."""
        for y in range(0, h, 4):
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, 30), width=1)

    def _draw_ui_overlay(
        self,
        draw: ImageDraw.ImageDraw,
        scene_num: int,
        title: str,
        narration: str,
        style_id: str,
        palette: Dict[str, Any],
        w: int,
        h: int
    ):
        """Diseña la barra inferior cinematográfica con tipografía y badge de escena."""
        overlay_h = 135
        # Fondo oscuro semitransparente con desenfoque de viñeta
        draw.rectangle([0, h - overlay_h, w, h], fill=(12, 16, 24, 220))
        # Borde de acento superior
        accent = palette.get("accent", (255, 200, 50))
        draw.line([(0, h - overlay_h), (w, h - overlay_h)], fill=(*accent, 220), width=2)

        # Badge de Escena
        badge_text = f"ESCENA {scene_num:02d} • 10s"
        badge_w = 150
        draw.rounded_rectangle([40, h - overlay_h + 16, 40 + badge_w, h - overlay_h + 44], radius=6, fill=(*accent, 255))
        draw.text((52, h - overlay_h + 20), badge_text, fill=(20, 20, 25), font=self._font_badge)

        # Título de escena
        clean_title = title if len(title) < 50 else title[:47] + "..."
        draw.text((40 + badge_w + 18, h - overlay_h + 17), clean_title, fill=(255, 255, 255), font=self._font_title)

        # Subtítulo / Narración en off (ajustado a 2 líneas si es largo)
        wrapped_narration = self._wrap_text(narration, max_chars=95)
        text_y = h - overlay_h + 54
        for line in wrapped_narration[:2]:
            draw.text((40, text_y), line, fill=(225, 230, 240), font=self._font_sub)
            text_y += 26

    def _wrap_text(self, text: str, max_chars: int = 90) -> list:
        words = text.split()
        lines = []
        current = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > max_chars:
                lines.append(" ".join(current))
                current = [w]
                cur_len = len(w)
            else:
                current.append(w)
                cur_len += len(w) + 1
        if current:
            lines.append(" ".join(current))
        return lines or [text]
