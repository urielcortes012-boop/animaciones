"""
Analizador inteligente de guiones para CineFlow AI.
Divide guiones completos en escenas de 10 segundos, extrayendo:
- Número de escena y título
- Narración / Diálogo (Voz en off)
- Indicaciones visuales y acción
- Personajes detectados
- Ambiente / Locación
- Estado emocional y duración fija (10s)
"""

import re
from typing import List, Dict, Any

class ScriptParser:
    @staticmethod
    def parse(script_text: str, default_duration: float = 10.0) -> List[Dict[str, Any]]:
        """
        Analiza el texto del guion y lo estructura en una lista de escenas.
        """
        clean_text = script_text.strip()
        if not clean_text:
            return []

        # Intentar dividir por encabezados explícitos de escenas:
        # Ej: "Escena 1:", "[Escena 1]", "Scene 1 -", "1. ", "ESCENA 1"
        scene_pattern = re.compile(
            r'(?:^|\n+)(?:(?:escena|scene|toma|cap[ií]tulo)\s*(\d+)[\s:\-\.]*|(\d+)[\.\-\)]\s+)(.*?)(?=(?:\n+(?:(?:escena|scene|toma|cap[ií]tulo)\s*\d+[\s:\-\.]*|\d+[\.\-\)]\s+))|$)',
            re.IGNORECASE | re.DOTALL
        )

        matches = list(scene_pattern.finditer(clean_text))
        scenes = []

        if matches and len(matches) > 1:
            for idx, match in enumerate(matches, start=1):
                raw_num = match.group(1) or match.group(2)
                scene_num = int(raw_num) if raw_num and raw_num.isdigit() else idx
                content = match.group(3).strip()
                if not content:
                    continue
                parsed_scene = ScriptParser._extract_scene_details(content, scene_num, default_duration)
                scenes.append(parsed_scene)
        else:
            # Si no hay marcadores explícitos de "Escena 1", dividir por párrafos dobles o bloques coherentes
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', clean_text) if p.strip()]
            
            if len(paragraphs) == 1:
                # Si es un solo párrafo largo, dividir por oraciones para crear escenas de ~10s
                sentences = re.split(r'(?<=[.!?])\s+', paragraphs[0])
                # Agrupar de 1 a 2 oraciones por escena de 10 segundos
                chunk = []
                chunk_len = 0
                temp_scenes = []
                for s in sentences:
                    s_clean = s.strip()
                    if not s_clean:
                        continue
                    chunk.append(s_clean)
                    chunk_len += len(s_clean.split())
                    if chunk_len >= 16: # ~16 a 25 palabras equivalen a ~8-10 segundos hablados
                        temp_scenes.append(" ".join(chunk))
                        chunk = []
                        chunk_len = 0
                if chunk:
                    temp_scenes.append(" ".join(chunk))
                paragraphs = temp_scenes or [clean_text]

            for idx, p in enumerate(paragraphs, start=1):
                parsed_scene = ScriptParser._extract_scene_details(p, idx, default_duration)
                scenes.append(parsed_scene)

        # Garantizar que al menos haya una escena si había texto
        if not scenes and clean_text:
            scenes.append(ScriptParser._extract_scene_details(clean_text, 1, default_duration))

        return scenes

    @staticmethod
    def _extract_scene_details(raw_content: str, scene_num: int, duration: float) -> Dict[str, Any]:
        """
        Extrae diálogo, descripción visual, personajes y atmósfera de una escena.
        """
        lines = [line.strip() for line in raw_content.split('\n') if line.strip()]
        
        title = f"Escena {scene_num}"
        narration = ""
        visual_desc = ""
        
        # Buscar patrones específicos como:
        # Visual: o Acción: o Descripción:
        # Audio: o Voz: o Diálogo: o Narración:
        narration_parts = []
        visual_parts = []
        
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if any(line_lower.startswith(prefix) for prefix in ['visual:', 'imagen:', 'descripción:', 'video:', 'acción:']):
                clean_line = re.sub(r'^(visual|imagen|descripción|video|acción):\s*', '', line, flags=re.IGNORECASE)
                visual_parts.append(clean_line)
            elif any(line_lower.startswith(prefix) for prefix in ['voz:', 'audio:', 'diálogo:', 'narración:', 'locución:', 'guion:']):
                clean_line = re.sub(r'^(voz|audio|diálogo|narración|locución|guion):\s*', '', line, flags=re.IGNORECASE)
                narration_parts.append(clean_line)
            else:
                # Si tiene comillas, suele ser diálogo/narración
                if line.startswith('"') and line.endswith('"'):
                    narration_parts.append(line.strip('"'))
                elif not narration_parts and len(lines) > 1 and idx == 0:
                    # Primera línea corta puede ser título
                    if len(line.split()) <= 6:
                        title = line
                    else:
                        narration_parts.append(line)
                else:
                    narration_parts.append(line)

        if narration_parts:
            narration = " ".join(narration_parts)
        else:
            narration = raw_content

        if visual_parts:
            visual_desc = " ".join(visual_parts)
        else:
            # Deduce la descripción visual a partir del texto
            visual_desc = narration

        # Detectar personajes básicos nombrados con Mayúscula inicial en el texto
        words = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b', raw_content)
        common_words = {'El', 'La', 'Los', 'Las', 'Un', 'Una', 'En', 'De', 'Por', 'Con', 'Cuando', 'Mientras', 'Pero', 'Y', 'O', 'Escena', 'Visual', 'Voz', 'Audio'}
        detected_chars = list(dict.fromkeys([w for w in words if w not in common_words]))

        # Detectar atmósfera o emoción
        mood = "cinematic"
        content_lower = raw_content.lower()
        if any(w in content_lower for w in ['bosque', 'árbol', 'naturaleza', 'paz', 'río', 'viento', 'pradera']):
            mood = "nature_peaceful"
        elif any(w in content_lower for w in ['lucha', 'batalla', 'corre', 'furia', 'impacto', 'peligro', 'espada']):
            mood = "action_epic"
        elif any(w in content_lower for w in ['misterio', 'sombra', 'portal', 'magia', 'extraño', 'secreto']):
            mood = "mystical_magic"
        elif any(w in content_lower for w in ['ciudad', 'neón', 'nave', 'robot', 'futuro', 'cibernético']):
            mood = "futuristic_tech"

        return {
            "scene_number": scene_num,
            "title": title,
            "narration": narration.strip(),
            "visual_desc": visual_desc.strip(),
            "duration": float(duration), # 10.0 segundos
            "detected_characters": detected_chars[:3],
            "mood": mood
        }
