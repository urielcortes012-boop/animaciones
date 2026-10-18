const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow = null;

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
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.removeMenu && mainWindow.removeMenu();

  // Cargar directamente el archivo index.html local (cero servidores, cero puertos, apertura instantánea)
  mainWindow.loadFile(path.join(__dirname, 'frontend', 'index.html'));
}

app.whenReady().then(() => {
  if (process.platform === 'darwin' && app.dock) {
    try {
      app.dock.setIcon(path.join(__dirname, 'build', 'icon.png'));
    } catch (e) {}
  }

  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
