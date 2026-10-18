"""
Motor de Coherencia Global (Story Bible & Coherence Anchor) para CineFlow AI.
Garantiza que los personajes, paletas de color, estilo de animación y voz
permanezcan idénticos y coherentes en todas las escenas del guion.
"""

from typing import Dict, Any, List
from .style_presets import STYLES

class CoherenceEngine:
    def __init__(self, style_id: str = "ghibli", voice_profile: Dict[str, Any] = None):
        self.style_id = style_id if style_id in STYLES else "ghibli"
        self.style = STYLES[self.style_id]
        self.voice_profile = voice_profile or {
            "mode": "natural",
            "pitch_shift": 1.0,
            "tempo": 1.0,
            "timbre_eq": [0, 0, 0]
        }
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.primary_protagonist: str = ""
        self.world_palette = self.style["palette"].copy()

    def build_story_bible(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analiza el guion completo para crear la "Biblia de Producción" que
        fija los tokens visuales y de voz de toda la obra.
        """
        all_chars = []
        for sc in scenes:
            all_chars.extend(sc.get("detected_characters", []))

        # Determinar el protagonista más recurrente o asignar uno por defecto
        if all_chars:
            from collections import Counter
            counts = Counter(all_chars)
            self.primary_protagonist = counts.most_common(1)[0][0]
        else:
            self.primary_protagonist = "Protagonista"

        # Asignar atributos coherentes al protagonista
        protagonist_card = {
            "name": self.primary_protagonist,
            "hair_color": self.style["palette"]["char_hair"],
            "clothes_color": self.style["palette"]["char_clothes"],
            "skin_color": self.style["palette"]["char_skin"],
            "accent_color": self.style["palette"]["accent"],
            "accessory": "Capa / Bufanda de viajero",
            "silhouette": "hero_dynamic"
        }
        self.characters[self.primary_protagonist] = protagonist_card

        # Crear personajes secundarios si existen
        for ch in dict.fromkeys(all_chars):
            if ch != self.primary_protagonist and ch not in self.characters:
                # Color complementario coherente
                self.characters[ch] = {
                    "name": ch,
                    "hair_color": (40, 40, 40),
                    "clothes_color": self.style["palette"]["accent"],
                    "skin_color": self.style["palette"]["char_skin"],
                    "accent_color": self.style["palette"]["char_clothes"],
                    "accessory": "Insignia distintiva",
                    "silhouette": "companion"
                }

        return {
            "style_id": self.style_id,
            "style_name": self.style["name"],
            "protagonist": protagonist_card,
            "characters": self.characters,
            "voice_profile": self.voice_profile,
            "world_palette": self.world_palette,
            "atmosphere": self.style["atmosphere"],
            "lighting": self.style["lighting"]
        }

    def enrich_scene_with_coherence(self, scene: Dict[str, Any], story_bible: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inyecta los anclajes de coherencia en cada escena individual
        para asegurar que el generador mantenga el mismo aspecto visual y sonoro.
        """
        enriched = scene.copy()
        enriched["coherence"] = {
            "style": story_bible["style_name"],
            "style_id": self.style_id,
            "palette": self.world_palette,
            "protagonist": story_bible["protagonist"],
            "active_character": story_bible["protagonist"], # Mantiene la figura principal
            "voice_profile": self.voice_profile,
            "lighting": story_bible["lighting"],
            "atmosphere": story_bible["atmosphere"]
        }
        return enriched
