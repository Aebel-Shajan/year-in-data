const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.cjs'),
            contextIsolation: true, // Important for security
            enableRemoteModule: false, // Disable remote module for security reasons
            nodeIntegration: false // Do not enable nodeIntegration for security reasons
        }
    });

    // Load the local web server URL
    mainWindow.loadURL('http://localhost:5173');

}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});