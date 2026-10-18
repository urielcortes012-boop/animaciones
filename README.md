# CineAnime Studio 🎬✨
### Estudio Especializado de Animación Anime Cinemático

**CineAnime Studio** es una herramienta de animación enfocada exclusivamente en la estética visual **Anime Seinen / Drama Realista** de la escena de referencia. Permite animar imágenes individuales con atmósfera viva cinemática o combinar secuencias de imágenes consecutivas para crear animaciones fluidas con control de FPS e interpolación.

---

## 🌟 Modos de Animación

### 1. ✨ Animación Cinemática de Escena (Luz, Atmósfera y Cámara 3D)
Anima una imagen fija (por defecto la escena de referencia o cualquier imagen en este estilo que subas) dándole vida con:
- **Luz Cenital Oscilante**: Simulación de la bombilla cálida del techo con sutiles variaciones de voltaje y sombras vivas.
- **Partículas Suspendidas en el Haz de Luz**: Motas de polvo flotantes que cruzan el cono de luz.
- **Movimiento de Cámara (Ken Burns)**: Paneo y zoom 3D continuo diseñado para un bucle perfecto (Loop).
- **Textura de Grano 35mm**: Acabado analógico cinematográfico característico de largometrajes de anime.
- **Exportación Dual**: Genera tanto video **MP4 (H.264)** como **GIF animado** listo para descargar.

### 2. 🎞️ Animador de Secuencias de Imágenes Consecutivas
Diseñado para conectar fotogramas continuos:
- **Subida de Múltiples Imágenes**: Arrastra o selecciona `frame_01.jpg`, `frame_02.jpg`, etc.
- **Ejemplo Pre-Cargado**: Incluye una secuencia de 4 fotogramas en el estilo anime listos para probar con 1 clic.
- **Tira de Fotogramas (Filmstrip)**: Vista previa con numeración (#1, #2...), reordenamiento y eliminación.
- **Control de Velocidad (FPS)**: 6 FPS (Boceto), 8 FPS (Anime limitado), 12 FPS (Estándar anime en 2s), 24 FPS (Cinemático fluido).
- **Modos de Bucle**: Bucle continuo o Ping-Pong (ida y vuelta).
- **Interpolación**: Corte directo (cel tradicional) o suavizado de movimiento (*Frame Blending*).

---

## 🚀 Cómo Iniciar la Aplicación

1. **Abrir la terminal en la carpeta del proyecto**:
   ```bash
   cd /Users/urielcortes/animaciones/animaciones
   ```

2. **Iniciar el servidor**:
   ```bash
   ./start.sh
   ```

3. **Abrir en tu navegador**:
   Visita: **[http://localhost:8000](http://localhost:8000)**

---

## 📂 Estructura del Proyecto

```
animaciones/
├── backend/
│   ├── app.py                     # Servidor FastAPI especializado
│   └── engine/
│       └── anime_animator.py      # Motor de animación cinemática y secuencias
├── frontend/
│   ├── index.html                 # Interfaz dark studio especializada
│   ├── styles.css                 # Estilos cinemáticos oscuros
│   └── app.js                     # Controlador interactivo, filmstrip y reproductor
├── assets/
│   ├── reference_anime.jpg        # Imagen de referencia del estilo visual
│   └── sample_sequence/           # 4 fotogramas consecutivos de ejemplo
├── outputs/                       # Videos MP4 y GIFs generados
└── README.md
```
