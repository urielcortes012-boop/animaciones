const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let pyProc = null;
let mainWindow = null;
const BACKEND_PORT = 8000;

function startBackend() {
  const backendScript = path.join(__dirname, 'backend', 'app.py');
  
  // Iniciar servidor FastAPI en segundo plano
  pyProc = spawn('python3', [backendScript], {
    env: { ...process.env, PORT: String(BACKEND_PORT) }
  });

  pyProc.stdout.on('data', (data) => {
    console.log(`[Python]: ${data}`);
  });

  pyProc.stderr.on('data', (data) => {
    console.error(`[Python Err]: ${data}`);
  });

  pyProc.on('close', (code) => {
    console.log(`[Python] cerrado con código: ${code}`);
  });
}

function waitForBackend(callback, retries = 30) {
  const check = () => {
    http.get(`http://127.0.0.1:${BACKEND_PORT}/api/reference_image`, (res) => {
      if (res.statusCode === 200) {
        callback();
      } else {
        retry();
      }
    }).on('error', () => {
      retry();
    });
  };

  const retry = () => {
    if (retries > 0) {
      retries--;
      setTimeout(check, 300);
    } else {
      console.warn("Backend no respondió en el tiempo límite, cargando ventana de todas formas...");
      callback();
    }
  };

  check();
}

function createWindow() {
  const iconPath = path.join(__dirname, 'build', 'icon.png');
  
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 880,
    minWidth: 1080,
    minHeight: 700,
    icon: iconPath,
    title: "CineAnime Studio",
    backgroundColor: "#0a0c10",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.removeMenu && mainWindow.removeMenu();

  waitForBackend(() => {
    mainWindow.loadURL(`http://127.0.0.1:${BACKEND_PORT}`);
  });
}

app.whenReady().then(() => {
  if (process.platform === 'darwin' && app.dock) {
    try {
      app.dock.setIcon(path.join(__dirname, 'build', 'icon.png'));
    } catch (e) {
      console.error('Error configurando icono del dock:', e);
    }
  }

  startBackend();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('will-quit', () => {
  if (pyProc) {
    try {
      pyProc.kill('SIGTERM');
    } catch (e) {}
    pyProc = null;
  }
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
