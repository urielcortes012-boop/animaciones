"""
Módulo de Clonación y Síntesis de Voz para CineFlow AI.
Permite:
1. Analizar muestras de audio grabadas con micrófono (WebM, WAV, Ogg, MP4) o subidas en archivo.
2. Extraer el perfil acústico (F0 tono base, formantes tímbricos, tempo y ganancia espectral)
   garantizando tipos nativos de Python para serialización JSON limpia.
3. Asignar la voz clonada al Narrador, al Protagonista, a personajes específicos o a Todos.
4. Modular tono y ecualización de formantes con FFmpeg y conector para ElevenLabs.
"""

import os
import uuid
import wave
import subprocess
import numpy as np
from typing import Dict, Any, Optional
from gtts import gTTS
import requests

class VoiceCloner:
    def __init__(self, upload_dir: str = "uploads", output_dir: str = "outputs"):
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

    def analyze_audio_sample(self, audio_path: str) -> Dict[str, Any]:
        """
        Convierte el audio a WAV mono y extrae características acústicas para la clonación.
        Garantiza que todos los valores devueltos sean floats/ints nativos de Python.
        """
        sample_id = str(uuid.uuid4())[:8]
        wav_path = os.path.join(self.upload_dir, f"sample_analyzed_{sample_id}.wav")
        
        # Convertir con ffmpeg a 24000Hz mono PCM (acepta webm, ogg, mp4, aac, wav)
        conv_cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-ac", "1", "-ar", "24000",
            wav_path
        ]
        res = subprocess.run(conv_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Error procesando audio con ffmpeg: {res.stderr}")

        # Leer audio y calcular espectro
        with wave.open(wav_path, "rb") as wf:
            n_frames = wf.getnframes()
            rate = wf.getframerate()
            raw_data = wf.readframes(n_frames)
            samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)

        if len(samples) == 0:
            return {
                "mode": "cloned",
                "detected_f0": 170.0,
                "pitch_shift": 1.0,
                "tempo": 1.0,
                "low_gain": 0.0,
                "mid_gain": 0.0,
                "high_gain": 0.0,
                "assigned_role": "narrator"
            }

        # Calcular FFT para detectar tono fundamental aproximado (F0)
        mid = len(samples) // 2
        chunk = samples[max(0, mid - rate): min(len(samples), mid + rate)]
        if len(chunk) < 512:
            chunk = samples

        fft_vals = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1.0 / rate)

        # Buscar pico en el rango de voz humana (80Hz a 400Hz)
        vocal_mask = (freqs >= 80) & (freqs <= 400)
        vocal_freqs = freqs[vocal_mask]
        vocal_fft = fft_vals[vocal_mask]

        detected_f0 = 165.0
        if len(vocal_fft) > 0 and np.max(vocal_fft) > 0:
            detected_f0 = float(vocal_freqs[np.argmax(vocal_fft)])

        # Base gTTS promedio es ~170Hz
        base_f0 = 170.0
        pitch_ratio = float(round(float(detected_f0) / base_f0, 3))
        # Limitar rango para mantener inteligibilidad natural (0.72 a 1.38)
        pitch_ratio = float(max(0.72, min(1.38, pitch_ratio)))

        # Analizar energía espectral en 3 bandas:
        low_energy = float(np.mean(fft_vals[(freqs >= 100) & (freqs <= 600)])) if np.any((freqs >= 100) & (freqs <= 600)) else 1.0
        mid_energy = float(np.mean(fft_vals[(freqs >= 1000) & (freqs <= 3000)])) if np.any((freqs >= 1000) & (freqs <= 3000)) else 1.0
        high_energy = float(np.mean(fft_vals[(freqs >= 3500) & (freqs <= 7000)])) if np.any((freqs >= 3500) & (freqs <= 7000)) else 1.0

        total = low_energy + mid_energy + high_energy + 1e-6
        low_norm = low_energy / total
        mid_norm = mid_energy / total
        high_norm = high_energy / total

        low_gain = float(round((low_norm - 0.33) * 12.0, 1))
        mid_gain = float(round((mid_norm - 0.33) * 12.0, 1))
        high_gain = float(round((high_norm - 0.33) * 12.0, 1))

        # Clasificación tímbrica amigable
        timbre_label = "Voz Cálida y Profunda" if low_gain > 1.5 else ("Voz Brillante y Clara" if high_gain > 1.5 else "Voz Equilibrada y Natural")

        profile = {
            "mode": "cloned",
            "detected_f0": float(round(float(detected_f0), 1)),
            "pitch_shift": pitch_ratio,
            "tempo": 1.0,
            "low_gain": low_gain,
            "mid_gain": mid_gain,
            "high_gain": high_gain,
            "timbre_label": timbre_label,
            "sample_path": wav_path,
            "assigned_role": "narrator" # Por defecto, voz del narrador
        }
        return profile

    def synthesize_scene_audio(
        self,
        text: str,
        output_file: str,
        scene_duration: float = 10.0,
        voice_profile: Optional[Dict[str, Any]] = None,
        elevenlabs_api_key: Optional[str] = None,
        scene_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Sintetiza la voz para una escena aplicando la voz clonada al rol asignado
        (Narrador, Protagonista o Todos) y voces complementarias para los demás.
        """
        temp_raw = output_file + ".raw.mp3"
        assigned_role = voice_profile.get("assigned_role", "narrator") if voice_profile else "narrator"

        # Detectar si la escena es principalmente diálogo de personaje o narración
        is_character_dialogue = bool(scene_context and scene_context.get("is_dialogue", False))
        speaker_name = (scene_context.get("speaker") or "").lower() if scene_context else ""

        # Determinar si esta escena específica debe usar la voz clonada
        should_use_cloned = False
        if not voice_profile or voice_profile.get("mode") != "cloned":
            should_use_cloned = False
        elif assigned_role == "all":
            should_use_cloned = True
        elif assigned_role == "narrator" and not is_character_dialogue:
            should_use_cloned = True
        elif assigned_role in ["protagonist", "lucas"] and (is_character_dialogue or "protagonista" in speaker_name or "lucas" in speaker_name):
            should_use_cloned = True
        elif assigned_role == speaker_name:
            should_use_cloned = True
        elif assigned_role == "narrator":
            # Si no es diálogo explícito con dos puntos, se considera narración
            should_use_cloned = True

        # Generar audio base con ElevenLabs (si hay API key) o gTTS
        if elevenlabs_api_key and voice_profile and voice_profile.get("elevenlabs_voice_id") and should_use_cloned:
            voice_id = voice_profile["elevenlabs_voice_id"]
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                if resp.status_code == 200:
                    with open(temp_raw, "wb") as f:
                        f.write(resp.content)
                else:
                    self._generate_local_tts(text, temp_raw)
            except Exception:
                self._generate_local_tts(text, temp_raw)
        else:
            self._generate_local_tts(text, temp_raw)

        # Configurar filtros según si usa la voz clonada o la voz complementaria
        if should_use_cloned and voice_profile:
            pitch = float(voice_profile.get("pitch_shift", 1.0))
            low_g = float(voice_profile.get("low_gain", 0))
            mid_g = float(voice_profile.get("mid_gain", 0))
            high_g = float(voice_profile.get("high_gain", 0))
        elif is_character_dialogue and assigned_role == "narrator":
            # La voz clonada es el narrador, así que el personaje usa un tono más juvenil/enérgico
            pitch = 1.10
            low_g = -1.0
            mid_g = 3.5
            high_g = 2.0
        elif not is_character_dialogue and assigned_role == "protagonist":
            # La voz clonada es el protagonista, así que el narrador usa un tono más profundo y cinematográfico
            pitch = 0.90
            low_g = 4.0
            mid_g = 1.0
            high_g = 0.5
        else:
            # Estándar natural
            pitch = 1.0
            low_g = 0.5
            mid_g = 1.0
            high_g = 0.5

        # Construir filtro de audio con FFmpeg
        filter_parts = []
        if abs(pitch - 1.0) > 0.02:
            sample_rate = 24000
            new_rate = int(sample_rate * pitch)
            tempo_comp = round(1.0 / pitch, 4)
            filter_parts.append(f"asetrate={new_rate},atempo={tempo_comp}")

        filter_parts.append(f"equalizer=f=320:t=q:w=1.2:g={low_g}")
        filter_parts.append(f"equalizer=f=1800:t=q:w=1.2:g={mid_g}")
        filter_parts.append(f"equalizer=f=4500:t=q:w=1.0:g={high_g}")
        filter_parts.append("compand=attacks=0.02:decays=0.15:points=-70/-70|-24/-12|0/-3")
        filter_parts.append(f"apad=pad_dur={scene_duration},afade=t=out:st={scene_duration - 0.5}:d=0.5")

        audio_filter = ",".join(filter_parts)

        cmd = [
            "ffmpeg", "-y", "-i", temp_raw,
            "-af", audio_filter,
            "-t", str(scene_duration),
            "-c:a", "aac", "-b:a", "192k",
            output_file
        ]
        
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(temp_raw):
            try:
                os.remove(temp_raw)
            except OSError:
                pass

        if proc.returncode != 0:
            fallback_cmd = [
                "ffmpeg", "-y", "-i", temp_raw,
                "-t", str(scene_duration),
                "-c:a", "aac", output_file
            ]
            subprocess.run(fallback_cmd, capture_output=True)

        return output_file

    def _generate_local_tts(self, text: str, output_path: str):
        """Genera audio base con síntesis de voz en español natural"""
        clean_text = text.strip()
        if not clean_text:
            clean_text = "Escena en curso."
        tts = gTTS(text=clean_text, lang="es", tld="com.mx", slow=False)
        tts.save(output_path)
