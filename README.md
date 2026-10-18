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

### Modo Local (Tu computadora)
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

## 💻 Aplicación de Escritorio (Descarga Directa estilo Play Store)

¡**CineAnime Studio** cuenta con instaladores de escritorio listos para instalar con doble clic, **sin necesidad de instalar Python, Node ni tocar la terminal** en la otra computadora!

### 📥 1. Cómo Descargar e Instalar en Cualquier Computadora

Entra a la sección de **[Releases de GitHub](https://github.com/urielcortes012-boop/animaciones/releases)**:
- 🪟 **Para Windows**: Descarga `CineAnime Studio-Setup-1.0.0.exe`, ábrelo e instálalo normalmente.
- 🍏 **Para Mac**: Descarga `CineAnime Studio-1.0.0.dmg`, arrástralo a tu carpeta de Aplicaciones y listo.

---

### ☁️ Compilación Automática en la Nube (GitHub Actions)

El repositorio incluye un flujo automatizado de **GitHub Actions** (`.github/workflows/build-and-release.yml`):
- **Cero esfuerzo manual**: Cada vez que se crea una versión (Tag `v1.0.0`, `v1.0.1`...), GitHub compila en sus propios servidores de Mac y Windows los instaladores `.dmg` y `.exe` y los adjunta automáticamente al Release para descarga pública.
- También puedes ir a la pestaña **Actions** en GitHub y pulsar **"Run workflow"** para generar los instaladores cuando quieras.

---

### 🛠️ Comandos de Construcción y Ejecución Local

Si deseas probarla o compilarla tú mismo en cualquier computadora:

1. **Instalar dependencias**:
   ```bash
   npm install
   ```

2. **Abrir la aplicación en modo desarrollo**:
   ```bash
   npm start
   ```

3. **Generar instalador para Mac (.dmg)**:
   ```bash
   npm run build:mac
   ```
   *(El instalador generado se guardará en la carpeta `dist/`)*

4. **Generar instalador para Windows (.exe)**:
   ```bash
   npm run build:win
   ```
   *(El instalador generado se guardará en la carpeta `dist/`)*

---

### 🌐 Despliegue en la Nube (Opcional - Enlace Web)

Si también prefieres acceder vía navegador web desde cualquier dispositivo sin instalar nada:
1. Entra a **[Render.com](https://render.com)** y conecta tu repositorio `animaciones`.
2. Selecciona **Web Service** gratuito; se usará el `Dockerfile` automáticamente.

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
