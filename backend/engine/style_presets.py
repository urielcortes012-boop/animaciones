"""
Estilos visuales de animación y paletas de coherencia para CineFlow AI.
Define las características estéticas para:
- Studio Ghibli
- Anime Clásico
- Pixel Art (16-bit)
- 3D Pixar Style
- Dibujos Animados (Cartoon)
- Acuarela Artística (Watercolor)
- Cyberpunk / Sci-Fi
- Cómic / Novela Gráfica
"""

STYLES = {
    "ghibli": {
        "id": "ghibli",
        "name": "Studio Ghibli",
        "subtitle": "Acuarelas pastorales, naturaleza viva y luz mágica de atardecer",
        "emoji": "🌿",
        "badge_color": "#48bb78",
        "palette": {
            "sky_top": (135, 206, 235),
            "sky_bottom": (255, 248, 220),
            "hills_far": (102, 153, 115),
            "hills_near": (56, 128, 77),
            "ground": (45, 95, 52),
            "accent": (255, 179, 71),
            "cloud": (255, 255, 250),
            "particles": (255, 240, 180), # Floating golden spores / dandelion seeds
            "char_skin": (255, 224, 189),
            "char_clothes": (70, 110, 160),
            "char_hair": (74, 44, 23),
            "text_color": (255, 255, 255),
            "text_stroke": (30, 50, 30)
        },
        "atmosphere": "dandelion_spores",
        "lighting": "golden_hour",
        "line_style": "soft_organic"
    },
    "anime": {
        "id": "anime",
        "name": "Anime Clásico / Shonen",
        "subtitle": "Cel-shading vibrante, speed lines y contraste dinámico",
        "emoji": "⚡",
        "badge_color": "#ed8936",
        "palette": {
            "sky_top": (30, 60, 140),
            "sky_bottom": (240, 120, 80),
            "hills_far": (60, 40, 90),
            "hills_near": (30, 25, 60),
            "ground": (20, 18, 40),
            "accent": (255, 230, 40),
            "cloud": (250, 220, 230),
            "particles": (255, 240, 100), # Energy sparks / speed streaks
            "char_skin": (255, 230, 205),
            "char_clothes": (220, 45, 45),
            "char_hair": (40, 35, 75),
            "text_color": (255, 255, 255),
            "text_stroke": (10, 10, 20)
        },
        "atmosphere": "speed_lines",
        "lighting": "high_contrast",
        "line_style": "sharp_cel"
    },
    "pixelart": {
        "id": "pixelart",
        "name": "Pixel Art Retro 16-Bit",
        "subtitle": "Estética arcade nostálgica, paletas indexadas y dithering",
        "emoji": "👾",
        "badge_color": "#9f7aea",
        "palette": {
            "sky_top": (24, 20, 56),
            "sky_bottom": (104, 56, 108),
            "hills_far": (68, 36, 88),
            "hills_near": (34, 32, 52),
            "ground": (20, 20, 30),
            "accent": (106, 190, 48),
            "cloud": (217, 160, 102),
            "particles": (153, 229, 80), # Floating retro pixel stars
            "char_skin": (238, 195, 154),
            "char_clothes": (91, 110, 225),
            "char_hair": (118, 66, 138),
            "text_color": (255, 255, 255),
            "text_stroke": (0, 0, 0)
        },
        "atmosphere": "pixel_grid",
        "lighting": "flat_dithered",
        "line_style": "pixelated"
    },
    "pixar3d": {
        "id": "pixar3d",
        "name": "3D Render Estilo Pixar",
        "subtitle": "Volúmenes suaves, oclusión ambiental cálida e iluminación cinematográfica",
        "emoji": "🧸",
        "badge_color": "#4299e1",
        "palette": {
            "sky_top": (70, 130, 210),
            "sky_bottom": (200, 225, 255),
            "hills_far": (85, 120, 165),
            "hills_near": (60, 145, 110),
            "ground": (45, 110, 80),
            "accent": (255, 140, 50),
            "cloud": (255, 255, 255),
            "particles": (255, 255, 255), # Soft ambient dust motes
            "char_skin": (255, 218, 185),
            "char_clothes": (230, 80, 50),
            "char_hair": (80, 50, 30),
            "text_color": (255, 255, 255),
            "text_stroke": (20, 30, 50)
        },
        "atmosphere": "soft_glow",
        "lighting": "volumetric_rim",
        "line_style": "smooth_3d"
    },
    "cartoon": {
        "id": "cartoon",
        "name": "Dibujos Animados Modernos",
        "subtitle": "Trazos audaces, colores primarios vivos y animación squash & stretch",
        "emoji": "🎨",
        "badge_color": "#f56565",
        "palette": {
            "sky_top": (100, 190, 255),
            "sky_bottom": (255, 240, 150),
            "hills_far": (130, 190, 70),
            "hills_near": (90, 170, 50),
            "ground": (65, 140, 40),
            "accent": (255, 70, 85),
            "cloud": (255, 255, 255),
            "particles": (255, 215, 0), # Fun cartoon stars
            "char_skin": (255, 220, 180),
            "char_clothes": (255, 80, 50),
            "char_hair": (40, 40, 40),
            "text_color": (255, 255, 255),
            "text_stroke": (20, 20, 20)
        },
        "atmosphere": "cartoon_bounce",
        "lighting": "flat_vibrant",
        "line_style": "thick_outline"
    },
    "watercolor": {
        "id": "watercolor",
        "name": "Acuarela Artística",
        "subtitle": "Pigmentos traslúcidos con bordes fluidos y textura de lienzo",
        "emoji": "🖌️",
        "badge_color": "#38b2ac",
        "palette": {
            "sky_top": (180, 210, 235),
            "sky_bottom": (245, 235, 220),
            "hills_far": (160, 180, 190),
            "hills_near": (130, 160, 140),
            "ground": (110, 140, 120),
            "accent": (220, 130, 120),
            "cloud": (245, 245, 240),
            "particles": (210, 225, 240), # Watercolor splashes / droplets
            "char_skin": (245, 220, 200),
            "char_clothes": (120, 140, 170),
            "char_hair": (90, 70, 60),
            "text_color": (255, 255, 255),
            "text_stroke": (60, 60, 70)
        },
        "atmosphere": "paper_grain",
        "lighting": "diffuse_wash",
        "line_style": "bleeding_edges"
    },
    "cyberpunk": {
        "id": "cyberpunk",
        "name": "Cyberpunk / Sci-Fi Neón",
        "subtitle": "Luces de neón cian/magenta, rascacielos holográficos y lluvia futurista",
        "emoji": "🌆",
        "badge_color": "#00f0ff",
        "palette": {
            "sky_top": (10, 10, 26),
            "sky_bottom": (35, 10, 55),
            "hills_far": (20, 15, 45),
            "hills_near": (15, 20, 40),
            "ground": (8, 8, 16),
            "accent": (0, 240, 255),
            "cloud": (60, 20, 80),
            "particles": (255, 0, 128), # Neon rain & digital embers
            "char_skin": (240, 215, 195),
            "char_clothes": (30, 30, 40),
            "char_hair": (0, 240, 255), # Neon cyan hair
            "text_color": (0, 240, 255),
            "text_stroke": (20, 5, 30)
        },
        "atmosphere": "digital_rain",
        "lighting": "neon_glow",
        "line_style": "synthetic_glow"
    },
    "comic": {
        "id": "comic",
        "name": "Cómic / Novela Gráfica",
        "subtitle": "Puntos benday, sombras entintadas noir y viñetas dinámicas",
        "emoji": "📖",
        "badge_color": "#ecc94b",
        "palette": {
            "sky_top": (250, 210, 60),
            "sky_bottom": (245, 240, 225),
            "hills_far": (150, 140, 150),
            "hills_near": (80, 80, 90),
            "ground": (30, 30, 35),
            "accent": (230, 50, 50),
            "cloud": (255, 255, 255),
            "particles": (40, 40, 40), # Halftone dots / ink splashes
            "char_skin": (255, 225, 200),
            "char_clothes": (40, 90, 180),
            "char_hair": (20, 20, 20),
            "text_color": (255, 255, 255),
            "text_stroke": (0, 0, 0)
        },
        "atmosphere": "halftone_dots",
        "lighting": "noir_ink",
        "line_style": "halftone_crosshatch"
    }
}
