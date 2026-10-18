/**
 * CineAnime Studio - Motor de Animación Autónomo en Cliente
 * 100% nativo en JavaScript y HTML5 Canvas (sin requerir servidores ni Python)
 * Máxima compatibilidad, apertura instantánea y cero pantallas negras.
 */

const state = {
  currentMode: "cinematic", // "cinematic" | "sequence"
  cinematicImg: null,
  cinematicImgLoaded: false,
  sequenceFrames: [], // [{ id, img, url, name }]
  isPlaying: false,
  activeEngine: null, // "cinematic" | "sequence"
  duration: 4.0,
  fps: 24,
  speed: 1.0,
  currentTime: 0,
  cameraIntensity: 0.04,
  enableLightFlicker: true,
  enableParticles: true,
  enableFilmGrain: true,
  sequenceFps: 12,
  sequenceLoopMode: "loop",
  sequenceInterpolation: "none",
  particles: []
};

// Canvas principal y contexto
let canvas, ctx;
let lastTimestamp = 0;
let animFrameId = null;
let grainCanvas = null;

document.addEventListener("DOMContentLoaded", () => {
  canvas = document.getElementById("mainCanvasPlayer");
  ctx = canvas.getContext("2d");

  // Crear textura de grano de película reutilizable
  initFilmGrainTexture();

  // Inicializar partículas para el haz de luz
  initParticles(35);

  // Inicializar pestañas y controles
  setupModeSwitching();
  setupCinematicMode();
  setupSequenceMode();
  setupPlayerControls();

  // Cargar imagen de referencia por defecto
  loadDefaultReferenceImage();

  // Cargar secuencia de 4 fotogramas de ejemplo
  loadSampleSequence();
});

/**
 * Textura de grano de película 35mm
 */
function initFilmGrainTexture() {
  grainCanvas = document.createElement("canvas");
  grainCanvas.width = 128;
  grainCanvas.height = 128;
  const gCtx = grainCanvas.getContext("2d");
  const imgData = gCtx.createImageData(128, 128);
  const data = imgData.data;
  for (let i = 0; i < data.length; i += 4) {
    const val = (Math.random() * 255) | 0;
    data[i] = val;
    data[i + 1] = val;
    data[i + 2] = val;
    data[i + 3] = 45; // opacidad suave
  }
  gCtx.putImageData(imgData, 0, 0);
}

/**
 * Inicialización de partículas flotantes
 */
function initParticles(count) {
  state.particles = [];
  const w = canvas ? canvas.width : 830;
  const h = canvas ? canvas.height : 576;
  for (let i = 0; i < count; i++) {
    state.particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.4,
      vy: 0.2 + Math.random() * 0.5,
      size: 1.2 + Math.random() * 2.2,
      baseAlpha: 0.3 + Math.random() * 0.5,
      seed: Math.random() * 100
    });
  }
}

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
 * Cargar imagen de referencia por defecto
 */
function loadDefaultReferenceImage() {
  const img = new Image();
  img.crossOrigin = "anonymous";
  img.src = "../assets/reference_anime.jpg";
  img.onload = () => {
    state.cinematicImg = img;
    state.cinematicImgLoaded = true;
    canvas.width = img.naturalWidth || 830;
    canvas.height = img.naturalHeight || 576;
    initParticles(35);
  };
  img.onerror = () => {
    // Fallback a ruta relativa simple
    const fallback = new Image();
    fallback.src = "assets/reference_anime.jpg";
    fallback.onload = () => {
      state.cinematicImg = fallback;
      state.cinematicImgLoaded = true;
      canvas.width = fallback.naturalWidth || 830;
      canvas.height = fallback.naturalHeight || 576;
      initParticles(35);
    };
  };
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
      const reader = new FileReader();
      reader.onload = (ev) => {
        const userImg = new Image();
        userImg.src = ev.target.result;
        userImg.onload = () => {
          state.cinematicImg = userImg;
          state.cinematicImgLoaded = true;
          previewImg.src = userImg.src;
          sourceLabel.textContent = `Imagen Subida: ${file.name}`;
          canvas.width = userImg.naturalWidth;
          canvas.height = userImg.naturalHeight;
          initParticles(35);
        };
      };
      reader.readAsDataURL(file);
    }
  });

  generateBtn.addEventListener("click", () => {
    state.duration = parseFloat(document.getElementById("cinematicDurationSelect").value) || 4.0;
    state.cameraIntensity = parseFloat(document.getElementById("cameraIntensitySelect").value) || 0.04;
    state.enableLightFlicker = document.getElementById("toggleLightFlicker").checked;
    state.enableParticles = document.getElementById("toggleParticles").checked;
    state.enableFilmGrain = document.getElementById("toggleFilmGrain").checked;

    startAnimation("cinematic");
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

  loadSampleBtn.addEventListener("click", () => loadSampleSequence());

  clearBtn.addEventListener("click", () => {
    state.sequenceFrames = [];
    renderFilmstrip();
  });

  generateSeqBtn.addEventListener("click", () => {
    state.sequenceFps = parseInt(document.getElementById("sequenceFpsSelect").value) || 12;
    state.sequenceLoopMode = document.getElementById("sequenceLoopModeSelect").value || "loop";
    state.sequenceInterpolation = document.getElementById("sequenceInterpolationSelect").value || "none";

    startAnimation("sequence");
  });
}

function addFilesToSequence(files) {
  const sorted = files.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: 'base' }));
  let loadedCount = 0;
  sorted.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.src = e.target.result;
      img.onload = () => {
        state.sequenceFrames.push({
          id: "f_" + Math.random().toString(36).substr(2, 9),
          img: img,
          url: img.src,
          name: file.name
        });
        loadedCount++;
        if (loadedCount === sorted.length) {
          renderFilmstrip();
        }
      };
    };
    reader.readAsDataURL(file);
  });
}

function loadSampleSequence() {
  const samplePaths = [
    "../assets/sample_sequence/frame_01.jpg",
    "../assets/sample_sequence/frame_02.jpg",
    "../assets/sample_sequence/frame_03.jpg",
    "../assets/sample_sequence/frame_04.jpg"
  ];

  state.sequenceFrames = [];
  let loaded = 0;
  samplePaths.forEach((path, idx) => {
    const img = new Image();
    img.src = path;
    img.onload = () => {
      state.sequenceFrames[idx] = {
        id: "sample_" + idx,
        img: img,
        url: path,
        name: `Fotograma ${idx + 1}`
      };
      loaded++;
      if (loaded === samplePaths.length) {
        renderFilmstrip();
      }
    };
    img.onerror = () => {
      // Fallback ruta sin ..
      const fallback = new Image();
      fallback.src = path.replace("../", "");
      fallback.onload = () => {
        state.sequenceFrames[idx] = {
          id: "sample_" + idx,
          img: fallback,
          url: fallback.src,
          name: `Fotograma ${idx + 1}`
        };
        loaded++;
        if (loaded === samplePaths.length) {
          renderFilmstrip();
        }
      };
    };
  });
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
    if (!frame) return;
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
 * Iniciar Animación en Canvas
 */
function startAnimation(type) {
  state.activeEngine = type;
  state.isPlaying = true;
  state.currentTime = 0;
  lastTimestamp = performance.now();

  // Interfaz
  document.getElementById("viewportPlaceholder").style.display = "none";
  document.getElementById("mainVideoPlayer").style.display = "none";
  canvas.style.display = "block";
  document.getElementById("playerControlsBar").style.display = "block";
  document.getElementById("downloadActions").style.display = "flex";
  document.getElementById("techSpecsGrid").style.display = "grid";

  const dot = document.getElementById("playerStatusDot");
  dot.classList.add("active");
  const subtitle = document.getElementById("playerSubtitle");

  if (type === "cinematic") {
    subtitle.textContent = "Animación Cinemática Activa • Bucle Continuo";
    document.getElementById("specResolution").textContent = `${canvas.width}x${canvas.height}`;
    document.getElementById("specFps").textContent = "24 FPS";
    document.getElementById("specDuration").textContent = `${state.duration.toFixed(1)}s`;
    document.getElementById("totalTimeLabel").textContent = formatTime(state.duration);
  } else {
    subtitle.textContent = `Secuencia Consecutiva Activa (${state.sequenceFrames.length} cuadros)`;
    const totalFrames = state.sequenceLoopMode === "ping_pong" 
      ? Math.max(1, state.sequenceFrames.length * 2 - 2) 
      : state.sequenceFrames.length;
    const seqDuration = totalFrames / state.sequenceFps;
    state.duration = seqDuration;
    document.getElementById("specResolution").textContent = `${state.sequenceFrames[0].img.naturalWidth}x${state.sequenceFrames[0].img.naturalHeight}`;
    document.getElementById("specFps").textContent = `${state.sequenceFps} FPS`;
    document.getElementById("specDuration").textContent = `${seqDuration.toFixed(1)}s`;
    document.getElementById("totalTimeLabel").textContent = formatTime(seqDuration);
  }

  document.getElementById("playPauseBtn").textContent = "⏸";

  if (animFrameId) cancelAnimationFrame(animFrameId);
  animFrameId = requestAnimationFrame(renderLoop);
}

/**
 * Bucle Principal de Renderizado (60 FPS interactivo)
 */
function renderLoop(timestamp) {
  const dt = (timestamp - lastTimestamp) / 1000;
  lastTimestamp = timestamp;

  if (state.isPlaying && dt > 0) {
    state.currentTime += dt * state.speed;
    if (state.currentTime >= state.duration) {
      state.currentTime = state.currentTime % state.duration;
    }
    updateTimelineUI();
  }

  // Dibujar fotograma según el motor activo
  if (state.activeEngine === "cinematic") {
    drawCinematicFrame(state.currentTime);
  } else if (state.activeEngine === "sequence") {
    drawSequenceFrame(state.currentTime);
  }

  animFrameId = requestAnimationFrame(renderLoop);
}

/**
 * Renderizado de Fotograma Cinemático (Luz, Ken Burns, Partículas, Grano)
 */
function drawCinematicFrame(t) {
  if (!state.cinematicImgLoaded || !state.cinematicImg) return;

  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const progress = (t % state.duration) / state.duration;

  // 1. Movimiento de Cámara Ken Burns (Paneo y Zoom 3D continuo sin saltos)
  const zoom = 1.0 + Math.sin(progress * Math.PI) * state.cameraIntensity;
  const panX = Math.sin(progress * 2 * Math.PI) * (w * 0.02 * (state.cameraIntensity / 0.04));
  const panY = Math.cos(progress * 2 * Math.PI) * (h * 0.015 * (state.cameraIntensity / 0.04));

  ctx.save();
  ctx.translate(w / 2 + panX, h / 2 + panY);
  ctx.scale(zoom, zoom);
  ctx.drawImage(state.cinematicImg, -w / 2, -h / 2, w, h);
  ctx.restore();

  // 2. Oscilación de Luz Cenital Cálida (Bombilla de techo)
  if (state.enableLightFlicker) {
    const flicker = 1.0 + Math.sin(t * 7.3) * 0.045 + Math.sin(t * 2.1) * 0.025;
    const spotX = w * 0.5;
    const spotY = h * 0.15;
    const grad = ctx.createRadialGradient(spotX, spotY, 20, spotX, spotY, h * 0.95);
    grad.addColorStop(0, `rgba(255, 215, 140, ${0.16 * flicker})`);
    grad.addColorStop(0.4, `rgba(255, 180, 90, ${0.08 * flicker})`);
    grad.addColorStop(1, "rgba(0, 0, 0, 0)");

    ctx.save();
    ctx.globalCompositeOperation = "screen";
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  }

  // 3. Partículas Suspendidas en el Haz de Luz
  if (state.enableParticles) {
    ctx.save();
    ctx.fillStyle = "#ffffff";
    const lightCenter = w * 0.5;

    state.particles.forEach(p => {
      p.y += p.vy;
      p.x += p.vx + Math.sin(p.y * 0.03 + t * 2) * 0.25;

      if (p.y > h) p.y = 0;
      if (p.x < 0) p.x = w;
      if (p.x > w) p.x = 0;

      // Intensidad mayor cuando cruza el cono de luz cenital
      const distToLight = Math.abs(p.x - lightCenter);
      const beamFactor = Math.max(0.2, 1.0 - (distToLight / (w * 0.45)));
      const alpha = p.baseAlpha * beamFactor * (0.8 + Math.sin(t * 4 + p.seed) * 0.2);

      ctx.globalAlpha = Math.min(1.0, Math.max(0.05, alpha));
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }

  // 4. Textura de Grano 35mm estilo Seinen
  if (state.enableFilmGrain && grainCanvas) {
    ctx.save();
    ctx.globalAlpha = 0.07;
    ctx.globalCompositeOperation = "overlay";
    const pattern = ctx.createPattern(grainCanvas, "repeat");
    ctx.fillStyle = pattern;
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  }
}

/**
 * Renderizado de Secuencia de Fotogramas Consecutivos
 */
function drawSequenceFrame(t) {
  if (state.sequenceFrames.length === 0) return;

  const frames = state.sequenceFrames;
  const n = frames.length;
  let order = [];

  if (state.sequenceLoopMode === "ping_pong") {
    for (let i = 0; i < n; i++) order.push(i);
    for (let i = n - 2; i > 0; i--) order.push(i);
  } else {
    for (let i = 0; i < n; i++) order.push(i);
  }

  const totalSteps = order.length;
  const frameDuration = 1 / state.sequenceFps;
  const totalSeqDuration = totalSteps * frameDuration;

  const curSec = t % totalSeqDuration;
  const stepIdx = Math.floor(curSec / frameDuration) % totalSteps;
  const frameIdx = order[stepIdx];
  const nextStepIdx = (stepIdx + 1) % totalSteps;
  const nextFrameIdx = order[nextStepIdx];

  const currentFrame = frames[frameIdx];
  const nextFrame = frames[nextFrameIdx];

  if (!currentFrame || !currentFrame.img) return;

  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  // Dibujar cuadro actual
  ctx.drawImage(currentFrame.img, 0, 0, w, h);

  // Interpolación / Frame Blending
  if (state.sequenceInterpolation === "blend" && nextFrame && nextFrame.img) {
    const fraction = (curSec % frameDuration) / frameDuration;
    ctx.save();
    ctx.globalAlpha = fraction;
    ctx.drawImage(nextFrame.img, 0, 0, w, h);
    ctx.restore();
  }
}

/**
 * Actualizar controles de tiempo y scrubber
 */
function updateTimelineUI() {
  const scrubber = document.getElementById("frameScrubber");
  const curLabel = document.getElementById("currentTimeLabel");
  if (state.duration > 0) {
    const pct = (state.currentTime / state.duration) * 100;
    scrubber.value = pct;
    curLabel.textContent = formatTime(state.currentTime);
  }
}

/**
 * Control del Reproductor de Video y Exportación
 */
function setupPlayerControls() {
  const playPauseBtn = document.getElementById("playPauseBtn");
  const stepBackBtn = document.getElementById("stepBackBtn");
  const stepFwdBtn = document.getElementById("stepFwdBtn");
  const scrubber = document.getElementById("frameScrubber");
  const speedSelect = document.getElementById("speedSelect");

  playPauseBtn.addEventListener("click", () => {
    state.isPlaying = !state.isPlaying;
    playPauseBtn.textContent = state.isPlaying ? "⏸" : "▶";
  });

  stepBackBtn.addEventListener("click", () => {
    state.isPlaying = false;
    playPauseBtn.textContent = "▶";
    const step = 1 / state.fps;
    state.currentTime = (state.currentTime - step + state.duration) % state.duration;
    updateTimelineUI();
  });

  stepFwdBtn.addEventListener("click", () => {
    state.isPlaying = false;
    playPauseBtn.textContent = "▶";
    const step = 1 / state.fps;
    state.currentTime = (state.currentTime + step) % state.duration;
    updateTimelineUI();
  });

  scrubber.addEventListener("input", (e) => {
    state.isPlaying = false;
    playPauseBtn.textContent = "▶";
    const pct = parseFloat(e.target.value) / 100;
    state.currentTime = pct * state.duration;
    document.getElementById("currentTimeLabel").textContent = formatTime(state.currentTime);
  });

  speedSelect.addEventListener("change", (e) => {
    state.speed = parseFloat(e.target.value) || 1.0;
  });

  // Botón Descargar Video (MP4 / WebM H.264)
  document.getElementById("downloadMp4Btn").addEventListener("click", (e) => {
    e.preventDefault();
    exportVideo();
  });

  // Botón Descargar GIF Animado
  document.getElementById("downloadGifBtn").addEventListener("click", (e) => {
    e.preventDefault();
    exportGif();
  });
}

/**
 * Exportar Video (MP4 / WebM) grabando 1 ciclo completo de Canvas
 */
function exportVideo() {
  showRenderOverlay("Grabando y exportando video cinemático...");
  
  // Guardar estado previo
  const wasPlaying = state.isPlaying;
  const prevTime = state.currentTime;
  const prevSpeed = state.speed;

  state.isPlaying = false;
  state.currentTime = 0;
  state.speed = 1.0;

  let stream = canvas.captureStream(24);
  let mime = "video/webm;codecs=vp9";
  if (MediaRecorder.isTypeSupported("video/mp4;codecs=avc1")) {
    mime = "video/mp4;codecs=avc1";
  } else if (MediaRecorder.isTypeSupported("video/mp4")) {
    mime = "video/mp4";
  } else if (MediaRecorder.isTypeSupported("video/webm;codecs=h264")) {
    mime = "video/webm;codecs=h264";
  }

  const recorder = new MediaRecorder(stream, { mimeType: mime });
  const chunks = [];

  recorder.ondataavailable = (e) => {
    if (e.data.size > 0) chunks.push(e.data);
  };

  recorder.onstop = () => {
    const isMp4 = mime.includes("mp4");
    const ext = isMp4 ? "mp4" : "webm";
    const blob = new Blob(chunks, { type: mime });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement("a");
    a.href = url;
    a.download = `CineAnime_Animation.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Restaurar estado
    state.isPlaying = wasPlaying;
    state.currentTime = prevTime;
    state.speed = prevSpeed;
    hideRenderOverlay();
  };

  recorder.start();

  // Simular reproducción exacta a 24 FPS durante 1 ciclo completo
  const totalFrames = Math.round(state.duration * 24);
  let curFrame = 0;
  const frameInterval = (state.duration / totalFrames);

  const stepExport = () => {
    if (curFrame < totalFrames) {
      state.currentTime = curFrame * frameInterval;
      if (state.activeEngine === "cinematic") {
        drawCinematicFrame(state.currentTime);
      } else {
        drawSequenceFrame(state.currentTime);
      }
      curFrame++;
      setTimeout(stepExport, 1000 / 24);
    } else {
      recorder.stop();
    }
  };

  stepExport();
}

/**
 * Exportar GIF Animado directamente en cliente
 */
function exportGif() {
  showRenderOverlay("Generando archivo GIF animado...");

  setTimeout(() => {
    try {
      // Escalar a un tamaño razonable para GIF (máx 640px de ancho)
      const scale = Math.min(1.0, 640 / canvas.width);
      const gw = Math.round(canvas.width * scale);
      const gh = Math.round(canvas.height * scale);

      const gifCanvas = document.createElement("canvas");
      gifCanvas.width = gw;
      gifCanvas.height = gh;
      const gCtx = gifCanvas.getContext("2d");

      const encoder = new window.SimpleGifEncoder(gw, gh);
      const fps = 12;
      const totalFrames = Math.min(48, Math.round(state.duration * fps));
      const frameStep = state.duration / totalFrames;

      for (let i = 0; i < totalFrames; i++) {
        const t = i * frameStep;
        if (state.activeEngine === "cinematic") {
          drawCinematicFrame(t);
        } else {
          drawSequenceFrame(t);
        }
        gCtx.drawImage(canvas, 0, 0, gw, gh);
        encoder.addFrame(gCtx, 1000 / fps);
      }

      const blob = encoder.buildBlob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "CineAnime_Animation.gif";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error("Error exportando GIF:", err);
      alert("Error exportando GIF: " + err.message);
    } finally {
      hideRenderOverlay();
    }
  }, 50);
}

function showRenderOverlay(text) {
  const overlay = document.getElementById("renderOverlay");
  document.getElementById("renderStatusText").textContent = text;
  overlay.style.display = "flex";
}

function hideRenderOverlay() {
  document.getElementById("renderOverlay").style.display = "none";
}

function formatTime(sec) {
  if (isNaN(sec) || sec < 0) sec = 0;
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  const ms = Math.floor((sec % 1) * 100);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(ms).padStart(2, "0")}`;
}
