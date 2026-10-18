/**
 * CineAnime Studio - Frontend Controller
 * Especializado en animación estilo anime seinen y secuencias de imágenes consecutivas.
 */

// Estado global de la aplicación
const state = {
  currentMode: "cinematic", // "cinematic" | "sequence"
  cinematicImageFile: null,
  cinematicImageUrl: "/assets/reference_anime.jpg",
  sequenceFrames: [], // [{ id, file, url, name }]
  isPlaying: false,
  fps: 24,
  duration: 4.0
};

document.addEventListener("DOMContentLoaded", () => {
  setupModeSwitching();
  setupCinematicMode();
  setupSequenceMode();
  setupPlayerControls();

  // Cargar secuencia de ejemplo por defecto para que esté lista
  loadSampleSequence();
});

/**
 * Conmutador entre Modo Cinemático y Modo Secuencia
 */
function setupModeSwitching() {
  const tabCinematic = document.getElementById("tabModeCinematic");
  const tabSequence = document.getElementById("tabModeSequence");
  const panelCinematic = document.getElementById("panelCinematic");
  const panelSequence = document.getElementById("panelSequence");

  tabCinematic.addEventListener("click", () => {
    state.currentMode = "cinematic";
    tabCinematic.classList.add("active");
    tabSequence.classList.remove("active");
    panelCinematic.classList.add("active");
    panelSequence.classList.remove("active");
  });

  tabSequence.addEventListener("click", () => {
    state.currentMode = "sequence";
    tabSequence.classList.add("active");
    tabCinematic.classList.remove("active");
    panelSequence.classList.add("active");
    panelCinematic.classList.remove("active");
  });
}

/**
 * Configuración del Modo 1: Animación Cinemática de Escena
 */
function setupCinematicMode() {
  const changeImgBtn = document.getElementById("changeImageBtn");
  const fileInput = document.getElementById("singleImageInput");
  const previewImg = document.getElementById("cinematicPreviewImg");
  const sourceLabel = document.getElementById("sourceLabel");
  const generateBtn = document.getElementById("generateCinematicBtn");

  changeImgBtn.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      state.cinematicImageFile = file;
      state.cinematicImageUrl = URL.createObjectURL(file);
      previewImg.src = state.cinematicImageUrl;
      sourceLabel.textContent = `Imagen Subida: ${file.name}`;
    }
  });

  generateBtn.addEventListener("click", async () => {
    const duration = parseFloat(document.getElementById("cinematicDurationSelect").value);
    const cameraIntensity = parseFloat(document.getElementById("cameraIntensitySelect").value);
    const lightFlicker = document.getElementById("toggleLightFlicker").checked;
    const particles = document.getElementById("toggleParticles").checked;
    const filmGrain = document.getElementById("toggleFilmGrain").checked;

    showRenderOverlay("Generando animación cinemática con efectos de luz y cámara...");
    generateBtn.disabled = true;

    const formData = new FormData();
    if (state.cinematicImageFile) {
      formData.append("image", state.cinematicImageFile);
    }
    formData.append("duration", duration);
    formData.append("fps", 24);
    formData.append("camera_intensity", cameraIntensity);
    formData.append("enable_light_flicker", lightFlicker);
    formData.append("enable_particles", particles);
    formData.append("enable_film_grain", filmGrain);

    try {
      const res = await fetch("/api/animate/cinematic", {
        method: "POST",
        body: formData
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Error en el servidor al generar video.");
      }
      const data = await res.json();
      loadResultIntoPlayer(data);
    } catch (err) {
      alert(`Error al generar la animación: ${err.message || err}`);
      console.error(err);
    } finally {
      hideRenderOverlay();
      generateBtn.disabled = false;
    }
  });
}

/**
 * Configuración del Modo 2: Secuencia de Imágenes Consecutivas
 */
function setupSequenceMode() {
  const dropzone = document.getElementById("sequenceDropzone");
  const fileInput = document.getElementById("sequenceFilesInput");
  const loadSampleBtn = document.getElementById("loadSampleSeqBtn");
  const clearBtn = document.getElementById("clearFramesBtn");
  const generateSeqBtn = document.getElementById("generateSequenceBtn");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--accent-amber)";
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "var(--border-subtle)";
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--border-subtle)";
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFilesToSequence(Array.from(e.dataTransfer.files));
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      addFilesToSequence(Array.from(e.target.files));
    }
  });

  loadSampleBtn.addEventListener("click", loadSampleSequence);

  clearBtn.addEventListener("click", () => {
    state.sequenceFrames = [];
    renderFilmstrip();
  });

  generateSeqBtn.addEventListener("click", async () => {
    if (state.sequenceFrames.length < 2) {
      alert("Por favor agrega al menos 2 imágenes consecutivas.");
      return;
    }

    const fps = parseInt(document.getElementById("sequenceFpsSelect").value);
    const loopMode = document.getElementById("sequenceLoopModeSelect").value;
    const interpolation = document.getElementById("sequenceInterpolationSelect").value;

    showRenderOverlay("Ensamblando secuencia consecutiva a " + fps + " FPS...");
    generateSeqBtn.disabled = true;

    const formData = new FormData();
    formData.append("fps", fps);
    formData.append("loop_mode", loopMode);
    formData.append("interpolation", interpolation);

    // Verificar si son imágenes locales o si estamos usando la muestra
    const hasUploadedFiles = state.sequenceFrames.some(f => f.file !== null);
    if (!hasUploadedFiles) {
      formData.append("use_sample", true);
    } else {
      formData.append("use_sample", false);
      state.sequenceFrames.forEach(f => {
        if (f.file) {
          formData.append("images", f.file);
        }
      });
    }

    try {
      const res = await fetch("/api/animate/sequence", {
        method: "POST",
        body: formData
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Error en el servidor al animar la secuencia.");
      }
      const data = await res.json();
      loadResultIntoPlayer(data);
    } catch (err) {
      alert(`Error al animar la secuencia: ${err.message || err}`);
      console.error(err);
    } finally {
      hideRenderOverlay();
      generateSeqBtn.disabled = false;
    }
  });
}

function addFilesToSequence(files) {
  // Ordenar por nombre de archivo para mantener el orden consecutivo
  const sorted = files.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }));
  sorted.forEach(file => {
    const frameObj = {
      id: "f_" + Math.random().toString(36).substr(2, 9),
      file: file,
      url: URL.createObjectURL(file),
      name: file.name
    };
    state.sequenceFrames.push(frameObj);
  });
  renderFilmstrip();
}

async function loadSampleSequence() {
  try {
    const res = await fetch("/api/sample_sequence");
    const data = await res.json();
    state.sequenceFrames = data.frames.map((url, idx) => ({
      id: "sample_" + idx,
      file: null,
      url: url,
      name: `Fotograma ${idx + 1}`
    }));
    renderFilmstrip();
  } catch (err) {
    console.error("Error cargando secuencia de ejemplo:", err);
  }
}

function renderFilmstrip() {
  const track = document.getElementById("filmstripTrack");
  const countLabel = document.getElementById("frameCountLabel");
  const generateSeqBtn = document.getElementById("generateSequenceBtn");

  countLabel.textContent = state.sequenceFrames.length;
  generateSeqBtn.disabled = state.sequenceFrames.length < 2;

  if (state.sequenceFrames.length === 0) {
    track.innerHTML = '<div class="track-empty">Carga o arrastra imágenes consecutivas para ver la tira de fotogramas.</div>';
    return;
  }

  track.innerHTML = "";
  state.sequenceFrames.forEach((frame, idx) => {
    const card = document.createElement("div");
    card.className = "frame-card";
    card.innerHTML = `
      <img src="${frame.url}" alt="${frame.name}">
      <span class="frame-idx-badge">#${idx + 1}</span>
      <button class="frame-del-btn" title="Eliminar fotograma">✕</button>
    `;

    card.querySelector(".frame-del-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      state.sequenceFrames.splice(idx, 1);
      renderFilmstrip();
    });

    track.appendChild(card);
  });
}

/**
 * Control del Reproductor de Video y Exportación
 */
function setupPlayerControls() {
  const video = document.getElementById("mainVideoPlayer");
  const playPauseBtn = document.getElementById("playPauseBtn");
  const stepBackBtn = document.getElementById("stepBackBtn");
  const stepFwdBtn = document.getElementById("stepFwdBtn");
  const scrubber = document.getElementById("frameScrubber");
  const speedSelect = document.getElementById("speedSelect");
  const curTimeLabel = document.getElementById("currentTimeLabel");
  const totalTimeLabel = document.getElementById("totalTimeLabel");

  playPauseBtn.addEventListener("click", () => {
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });

  video.addEventListener("play", () => {
    playPauseBtn.textContent = "⏸";
    state.isPlaying = true;
  });

  video.addEventListener("pause", () => {
    playPauseBtn.textContent = "▶";
    state.isPlaying = false;
  });

  video.addEventListener("timeupdate", () => {
    if (!video.duration) return;
    const pct = (video.currentTime / video.duration) * 100;
    scrubber.value = pct;
    curTimeLabel.textContent = formatTime(video.currentTime);
  });

  video.addEventListener("loadedmetadata", () => {
    totalTimeLabel.textContent = formatTime(video.duration);
    scrubber.max = 100;
    scrubber.value = 0;
  });

  scrubber.addEventListener("input", (e) => {
    if (!video.duration) return;
    const targetTime = (e.target.value / 100) * video.duration;
    video.currentTime = targetTime;
  });

  // Paso de un fotograma hacia adelante o atrás
  stepFwdBtn.addEventListener("click", () => {
    video.pause();
    const frameTime = 1.0 / (state.fps || 24);
    video.currentTime = Math.min(video.duration, video.currentTime + frameTime);
  });

  stepBackBtn.addEventListener("click", () => {
    video.pause();
    const frameTime = 1.0 / (state.fps || 24);
    video.currentTime = Math.max(0, video.currentTime - frameTime);
  });

  // Selector de velocidad
  speedSelect.addEventListener("change", (e) => {
    video.playbackRate = parseFloat(e.target.value);
  });
}

function loadResultIntoPlayer(data) {
  const video = document.getElementById("mainVideoPlayer");
  const source = document.getElementById("mainVideoSource");
  const placeholder = document.getElementById("viewportPlaceholder");
  const controlsBar = document.getElementById("playerControlsBar");
  const specsGrid = document.getElementById("techSpecsGrid");
  const downloadActions = document.getElementById("downloadActions");
  const downloadMp4Btn = document.getElementById("downloadMp4Btn");
  const downloadGifBtn = document.getElementById("downloadGifBtn");
  const statusDot = document.getElementById("playerStatusDot");
  const subtitle = document.getElementById("playerSubtitle");

  state.fps = data.fps || 24;
  state.duration = data.duration || 4.0;

  // Actualizar fuente
  source.src = data.mp4_url;
  video.load();
  video.play().catch(() => {});

  placeholder.style.display = "none";
  controlsBar.style.display = "block";
  specsGrid.style.display = "grid";
  downloadActions.style.display = "flex";
  statusDot.classList.add("active");

  subtitle.textContent = `Animación lista (${data.duration}s a ${data.fps} FPS)`;

  // Configurar botones de descarga
  downloadMp4Btn.href = `/api/download/${data.mp4_file}`;
  downloadGifBtn.href = `/api/download/${data.gif_file}`;

  // Actualizar especificaciones
  document.getElementById("specResolution").textContent = `${data.width}x${data.height}`;
  document.getElementById("specFps").textContent = `${data.fps} FPS`;
  document.getElementById("specDuration").textContent = `${data.duration}s`;
}

function showRenderOverlay(msg) {
  const overlay = document.getElementById("renderOverlay");
  const text = document.getElementById("renderStatusText");
  text.textContent = msg;
  overlay.style.display = "flex";
}

function hideRenderOverlay() {
  document.getElementById("renderOverlay").style.display = "none";
}

function formatTime(seconds) {
  if (isNaN(seconds)) return "00:00.00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const millis = Math.floor((seconds % 1) * 100);
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${String(millis).padStart(2, "0")}`;
}
