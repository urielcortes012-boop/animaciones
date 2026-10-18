const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const net = require('net');
const { spawn } = require('child_process');
const http = require('http');

let pyProc = null;
let mainWindow = null;
let actualPort = 8000;

function findPythonExecutable() {
  const isWin = process.platform === 'win32';
  if (isWin) {
    const winCandidates = [
      'python',
      'py',
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python312', 'python.exe'),
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe'),
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python310', 'python.exe'),
      'C:\\Python312\\python.exe',
      'C:\\Python311\\python.exe',
      'C:\\Python310\\python.exe'
    ];
    for (const c of winCandidates) {
      if (c === 'python' || c === 'py' || fs.existsSync(c)) return c;
    }
    return 'python';
  } else {
    // macOS / Linux: buscar rutas completas para evitar problemas de PATH en Finder
    const macCandidates = [
      '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3',
      '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',
      '/Library/Frameworks/Python.framework/Versions/3.10/bin/python3',
      '/opt/homebrew/bin/python3',
      '/usr/local/bin/python3',
      '/usr/bin/python3',
      'python3',
      'python'
    ];
    for (const c of macCandidates) {
      if (fs.existsSync(c)) return c;
    }
    return 'python3';
  }
}

function getAvailablePort(startPort, callback) {
  // Primero comprobar si CineAnime Studio ya está corriendo en este puerto
  const req = http.get(`http://127.0.0.1:${startPort}/api/reference_image`, (res) => {
    if (res.statusCode === 200) {
      console.log(`[Backend]: Servidor ya activo en puerto ${startPort}`);
      return callback(startPort, true);
    }
    testPortAvailable(startPort, callback);
  });
  req.on('error', () => {
    testPortAvailable(startPort, callback);
  });
}

function testPortAvailable(port, callback) {
  const server = net.createServer();
  server.listen(port, '127.0.0.1', () => {
    server.once('close', () => callback(port, false));
    server.close();
  });
  server.on('error', () => {
    testPortAvailable(port + 1, callback);
  });
}

function startBackend(portToUse) {
  const binaryName = process.platform === 'win32' ? 'cineanime-backend.exe' : 'cineanime-backend';
  
  // Posibles rutas si está empaquetado como binario autónomo (producción)
  const candidateBinaries = [
    path.join(process.resourcesPath || '', 'backend_bin', binaryName),
    path.join(process.resourcesPath || '', 'backend_bin', 'cineanime-backend', binaryName),
    path.join(__dirname, 'backend_bin', binaryName),
    path.join(__dirname, 'backend_bin', 'cineanime-backend', binaryName)
  ];

  let execCmd = null;
  let execArgs = [];

  for (const binPath of candidateBinaries) {
    if (fs.existsSync(binPath)) {
      execCmd = binPath;
      execArgs = [];
      console.log(`[Backend]: Usando binario autónomo en ${execCmd}`);
      break;
    }
  }

  if (!execCmd) {
    const pythonCmd = findPythonExecutable();
    const backendScript = path.join(__dirname, 'backend', 'app.py');
    execCmd = pythonCmd;
    execArgs = [backendScript];
    console.log(`[Backend]: Usando Python (${execCmd}) en puerto ${portToUse}`);
  }

  const extraPath = process.platform === 'darwin'
    ? ':/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:/Library/Frameworks/Python.framework/Versions/3.11/bin'
    : '';

  pyProc = spawn(execCmd, execArgs, {
    env: {
      ...process.env,
      PORT: String(portToUse),
      PATH: (process.env.PATH || '') + extraPath
    }
  });

  pyProc.stdout.on('data', (data) => {
    console.log(`[Backend]: ${data}`);
  });

  pyProc.stderr.on('data', (data) => {
    console.error(`[Backend Err]: ${data}`);
  });

  pyProc.on('close', (code) => {
    console.log(`[Backend] cerrado con código: ${code}`);
  });
}

function waitForBackend(port, callback, retries = 40) {
  const check = () => {
    http.get(`http://127.0.0.1:${port}/api/reference_image`, (res) => {
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
      console.warn("Backend no respondió en el tiempo límite, cargando interfaz...");
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
    show: false,
    icon: iconPath,
    title: "CineAnime Studio",
    backgroundColor: "#0a0c10",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.removeMenu && mainWindow.removeMenu();

  getAvailablePort(8000, (port, alreadyRunning) => {
    actualPort = port;
    if (!alreadyRunning) {
      startBackend(actualPort);
    }

    waitForBackend(actualPort, () => {
      mainWindow.loadURL(`http://127.0.0.1:${actualPort}`);
      mainWindow.once('ready-to-show', () => {
        mainWindow.show();
      });
      setTimeout(() => {
        if (mainWindow && !mainWindow.isVisible()) {
          mainWindow.show();
        }
      }, 2000);
    });
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
