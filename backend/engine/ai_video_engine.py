"""
Motor de Generación de Video con Inteligencia Artificial Cinematográfica (BytePlus Seedance / ModelArk / Kling / Replicate).
Permite conectar CineFlow AI con modelos de difusión de video generativo de clase mundial:
- BytePlus ModelArk (Dreamina Seedance 2.0 / 2.5 de ByteDance)
- Replicate / Fal.ai (Kling AI, MiniMax Hailuo, Luma Ray, CogVideoX)
- Generación de escenas cinematográficas de alta definición con movimiento de cámara 3D
"""

import os
import time
import requests
from typing import Dict, Any, Optional

class AIVideoEngine:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_byteplus_scene(
        self,
        prompt: str,
        style_name: str,
        output_file: str,
        api_key: str,
        duration: int = 10,
        model_name: str = "dreamina-seedance-2.5"
    ) -> str:
        """
        Envía una tarea de generación a la API de BytePlus ModelArk (Seedance de ByteDance),
        monitorea su progreso asíncrono y descarga el video cinematográfico resultante.
        """
        endpoint = "https://modelark.byteplus.com/contents/generations/tasks"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Prompt enriquecido con coherencia estilística
        full_prompt = f"{style_name} cinematic aesthetic, 4k resolution, high dynamic range, masterwork animation. {prompt}"

        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "duration": duration,
            "aspect_ratio": "16:9",
            "fps": 30
        }

        # 1. Crear tarea de generación
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=20)
        if resp.status_code not in [200, 201]:
            raise RuntimeError(f"Error en API BytePlus ({resp.status_code}): {resp.text}")

        task_data = resp.json()
        task_id = task_data.get("id") or task_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"Respuesta inesperada de BytePlus: {task_data}")

        # 2. Monitorear progreso (polling)
        poll_url = f"{endpoint}/{task_id}"
        video_url = None
        max_attempts = 60 # hasta 5 minutos de renderizado
        for _ in range(max_attempts):
            time.sleep(5)
            status_resp = requests.get(poll_url, headers=headers, timeout=15)
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                status = status_data.get("status")
                if status == "succeeded":
                    video_url = status_data.get("result", {}).get("video_url") or status_data.get("video_url")
                    break
                elif status == "failed":
                    raise RuntimeError(f"La tarea de BytePlus falló: {status_data.get('error', 'Desconocido')}")

        if not video_url:
            raise TimeoutError("Tiempo de espera agotado generando video con BytePlus Seedance.")

        # 3. Descargar el archivo MP4 generado
        v_resp = requests.get(video_url, stream=True, timeout=30)
        with open(output_file, "wb") as f:
            for chunk in v_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return output_file

    def generate_replicate_scene(
        self,
        prompt: str,
        style_name: str,
        output_file: str,
        api_key: str,
        duration: int = 10,
        model_version: str = "kwaivgi/kling-v1"
    ) -> str:
        """
        Genera una escena de video con difusión de IA a través de Replicate (Kling AI / Luma / Minimax).
        """
        endpoint = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }

        full_prompt = f"Cinematic {style_name} animation, masterpiece, fluid motion, vivid colors: {prompt}"
        payload = {
            "version": model_version,
            "input": {
                "prompt": full_prompt,
                "duration": duration,
                "aspect_ratio": "16:9"
            }
        }

        resp = requests.post(endpoint, json=payload, headers=headers, timeout=20)
        if resp.status_code not in [200, 201]:
            raise RuntimeError(f"Error en API Replicate ({resp.status_code}): {resp.text}")

        pred_data = resp.json()
        poll_url = pred_data.get("urls", {}).get("get") or f"{endpoint}/{pred_data.get('id')}"

        video_url = None
        for _ in range(60):
            time.sleep(5)
            poll_resp = requests.get(poll_url, headers=headers, timeout=15)
            if poll_resp.status_code == 200:
                p_data = poll_resp.json()
                if p_data.get("status") == "succeeded":
                    output = p_data.get("output")
                    video_url = output if isinstance(output, str) else output[0]
                    break
                elif p_data.get("status") == "failed":
                    raise RuntimeError(f"Fallo en Replicate: {p_data.get('error')}")

        if not video_url:
            raise TimeoutError("Tiempo de espera agotado generando video en Replicate.")

        v_resp = requests.get(video_url, stream=True, timeout=30)
        with open(output_file, "wb") as f:
            for chunk in v_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return output_file
