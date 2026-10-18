# 🎬 CineAnime Studio - Estudio de Animación Cinemática

<div align="center">
  <img src="assets/reference_anime.jpg" alt="CineAnime Logo" width="130" style="border-radius: 50%;">
  <h3>Estudio Especializado de Animación Anime Cinemático</h3>
  <p>Software de escritorio de alta fidelidad para dar vida a escenas e imágenes consecutivas en la estética Seinen / Drama Realista sin necesidad de internet.</p>

  <p>
    <a href="https://github.com/urielcortes012-boop/animaciones/releases/latest">
      <img src="https://img.shields.io/badge/Versi%C3%B3n-1.0.0-6366f1?style=for-the-badge" alt="Versión">
    </a>
    <img src="https://img.shields.io/badge/Plataformas-macOS%20%7C%20Windows-22c55e?style=for-the-badge" alt="Plataformas">
    <img src="https://img.shields.io/badge/Modo-100%25%20Offline-f59e0b?style=for-the-badge" alt="Offline">
  </p>
</div>

---

## 📥 Descargas Rápidas (Instaladores Oficiales)

Descarga la versión lista para instalar en tu computadora:

| Sistema Operativo | Instalador | Formato | Enlace Directo |
| :--- | :--- | :--- | :--- |
| **🍎 macOS** | Versión 1.0.0 | `.dmg` | [**Descargar para Mac**](https://github.com/urielcortes012-boop/animaciones/releases/download/v1.0.0/CineAnime.Studio-1.0.0.dmg) *(~92 MB)* |
| **🪟 Windows** | Versión 1.0.0 | `.exe` | [**Descargar para Windows**](https://github.com/urielcortes012-boop/animaciones/releases/download/v1.0.0/CineAnime.Studio.Setup.1.0.0.exe) *(~85 MB)* |

> 📌 También puedes ver todas las versiones y notas de actualización en la [sección de Releases](https://github.com/urielcortes012-boop/animaciones/releases).

---

## 🚀 Guía de Instalación

### 🍎 En macOS
1. Descarga el archivo [`CineAnime.Studio-1.0.0.dmg`](https://github.com/urielcortes012-boop/animaciones/releases/download/v1.0.0/CineAnime.Studio-1.0.0.dmg).
2. Abre el archivo `.dmg` con doble clic.
3. Arrastra el icono de **CineAnime Studio** hacia tu carpeta de **Aplicaciones**.
4. *(Primera ejecución)*: Si macOS te muestra una advertencia de desarrollador no verificado, haz **clic derecho** sobre la aplicación en Aplicaciones y selecciona **"Abrir"**.

### 🪟 En Windows
1. Descarga el archivo [`CineAnime.Studio.Setup.1.0.0.exe`](https://github.com/urielcortes012-boop/animaciones/releases/download/v1.0.0/CineAnime.Studio.Setup.1.0.0.exe).
2. Haz doble clic en el instalador y sigue las instrucciones en pantalla.
3. *(Aviso SmartScreen)*: Si aparece la pantalla azul *"Windows protegió su PC"*, pulsa en **"Más información"** y luego en **"Ejecutar de todas formas"**.
4. Se creará automáticamente un acceso directo en tu Escritorio y Menú Inicio.

---

## ✨ Características Principales

- 🎞️ **Animador de Secuencias de Imágenes Consecutivas**:
  - Subida de fotogramas seriados (`frame_01.jpg`, `frame_02.jpg`...).
  - Incluye secuencia de 4 fotogramas anime de prueba precargada.
  - Tira de fotogramas (*filmstrip*) interactiva con reordenamiento y eliminación.
  - Control de velocidad: **6 FPS**, **8 FPS**, **12 FPS** (anime en 2s), y **24 FPS** (cinemático).
  - Modos de bucle continuo (*Loop*) y vaivén (*Ping-Pong*).
  - Interpolación: corte directo de cel tradicional o suavizado de fotogramas (*Frame Blending*).

- ✨ **Animación Cinemática de Escena**:
  - Oscilación de luz cenital con variaciones de voltaje de bombilla cálida.
  - Partículas de polvo flotantes que cruzan el cono luminoso.
  - Movimiento 3D de cámara tipo Ken Burns continuo y sin cortes.
  - Textura analógica de grano de película 35mm.

- 🎬 **Exportación Dual Instantánea**:
  - Video **MP4 (H.264)** de alta calidad con compatibilidad universal.
  - **GIF animado** optimizado con paleta personalizada de 128 colores.

- 🔌 **100% Autónomo y Offline**:
  - Toda la renderización se realiza localmente en tu equipo sin depender de internet ni servidores de terceros.

---

## 🛠️ Instalación para Desarrolladores

Si deseas clonar el proyecto para modificar o auditar el código:

```bash
# 1. Clonar el repositorio
git clone https://github.com/urielcortes012-boop/animaciones.git
cd animaciones

# 2. Instalar dependencias
npm install
pip install -r requirements.txt

# 3. Iniciar en modo desarrollo
npm start

# 4. Compilar instaladores
npm run build:mac   # Genera instalador .dmg para macOS
npm run build:win   # Genera instalador .exe para Windows
```

---

## ☁️ Compilación Automática (GitHub Actions)

El repositorio incluye integración continua con **GitHub Actions** (`.github/workflows/build-and-release.yml`):
- Al etiquetar una nueva versión (ej. `v1.0.0`), GitHub crea máquinas virtuales de Windows y Mac en la nube, compila los instaladores `.exe` y `.dmg`, y los publica automáticamente en la sección de Releases sin necesidad de compilar manualmente en múltiples computadoras.

---

<div align="center">
  <sub>Desarrollado por <b>Uriel Cortés</b> • CineAnime Studio</sub>
</div>
