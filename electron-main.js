const { app, BrowserWindow, ipcMain, dialog, Menu, Tray, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Global references
let mainWindow;
let splashWindow;
let pythonProcess;
let tray;
let isQuitting = false;
let currentMode = null; // 'demo' or 'live'

// Auto-updater configuration
autoUpdater.checkForUpdatesAndNotify();
autoUpdater.on('update-available', () => {
    dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'Update Available',
        message: 'A new version is available. It will be downloaded in the background.',
        buttons: ['OK']
    });
});

autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
        type: 'info',
        title: 'Update Ready',
        message: 'Update downloaded. The application will restart to apply the update.',
        buttons: ['Restart Now', 'Later']
    }).then((result) => {
        if (result.response === 0) {
            autoUpdater.quitAndInstall();
        }
    });
});

// Create splash/mode selector window
function createSplashWindow() {
    splashWindow = new BrowserWindow({
        width: 600,
        height: 700,
        frame: false,
        resizable: false,
        transparent: true,
        alwaysOnTop: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'electron-preload.js')
        },
        icon: path.join(__dirname, 'electron-ui', 'assets', 'icon.png')
    });

    splashWindow.loadFile(path.join(__dirname, 'electron-ui', 'splash.html'));

    splashWindow.on('closed', () => {
        splashWindow = null;
    });
}

// Create main application window
function createMainWindow(mode) {
    currentMode = mode;

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        show: false,
        frame: false,
        titleBarStyle: 'hidden',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'electron-preload.js')
        },
        icon: path.join(__dirname, 'electron-ui', 'assets', 'icon.png')
    });

    // Create custom menu bar
    mainWindow.loadFile(path.join(__dirname, 'electron-ui', 'main-window.html'));

    mainWindow.once('ready-to-show', () => {
        if (splashWindow) {
            setTimeout(() => {
                splashWindow.close();
                mainWindow.show();
            }, 500);
        } else {
            mainWindow.show();
        }
    });

    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Create system tray
    createTray();
}

// Create system tray icon
function createTray() {
    tray = new Tray(path.join(__dirname, 'electron-ui', 'assets', 'tray-icon.png'));

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'Show Application',
            click: () => {
                mainWindow.show();
            }
        },
        {
            label: `Mode: ${currentMode === 'demo' ? 'Demo Trading' : 'Live Trading'}`,
            enabled: false
        },
        { type: 'separator' },
        {
            label: 'Start Bot',
            click: () => {
                startPythonBackend();
            }
        },
        {
            label: 'Stop Bot',
            click: () => {
                stopPythonBackend();
            }
        },
        { type: 'separator' },
        {
            label: 'Check for Updates',
            click: () => {
                autoUpdater.checkForUpdatesAndNotify();
            }
        },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('Trading Bot Pro');
    tray.setContextMenu(contextMenu);

    tray.on('double-click', () => {
        mainWindow.show();
    });
}

// Start Python backend process
function startPythonBackend() {
    if (pythonProcess) {
        return;
    }

    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(__dirname, 'pocket_option_trading_bot', 'main.py');

    // Set environment variable for demo/live mode
    const env = { ...process.env, TRADING_MODE: currentMode };

    pythonProcess = spawn(pythonPath, [scriptPath], {
        cwd: path.join(__dirname, 'pocket_option_trading_bot'),
        env: env
    });

    pythonProcess.stdout.on('data', (data) => {
        // Send output to renderer process for terminal display
        if (mainWindow) {
            mainWindow.webContents.send('terminal-output', data.toString());
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        if (mainWindow) {
            mainWindow.webContents.send('terminal-output', data.toString());
        }
    });

    pythonProcess.on('close', (code) => {
        pythonProcess = null;
        if (mainWindow) {
            mainWindow.webContents.send('backend-status', 'stopped');
        }
    });

    if (mainWindow) {
        mainWindow.webContents.send('backend-status', 'running');
    }
}

// Stop Python backend process
function stopPythonBackend() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
    }
}

// IPC handlers
ipcMain.handle('select-mode', async (event, mode) => {
    createMainWindow(mode);
});

ipcMain.handle('start-backend', async () => {
    startPythonBackend();
    return true;
});

ipcMain.handle('stop-backend', async () => {
    stopPythonBackend();
    return true;
});

ipcMain.handle('get-mode', async () => {
    return currentMode;
});

ipcMain.handle('minimize-window', async () => {
    mainWindow.minimize();
});

ipcMain.handle('maximize-window', async () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow.maximize();
    }
});

ipcMain.handle('close-window', async () => {
    mainWindow.hide();
});

ipcMain.handle('open-flask', async () => {
    shell.openExternal('http://localhost:5000');
});

ipcMain.handle('check-env-file', async () => {
    const envPath = path.join(__dirname, 'pocket_option_trading_bot', '.env');
    return fs.existsSync(envPath);
});

ipcMain.handle('create-env-file', async (event, credentials) => {
    const envPath = path.join(__dirname, 'pocket_option_trading_bot', '.env');
    const envContent = `# Trading Bot Credentials
POCKET_OPTION_EMAIL=${credentials.email}
POCKET_OPTION_PASSWORD=${credentials.password}
${credentials.openaiKey ? `OPENAI_API_KEY=${credentials.openaiKey}` : '# OPENAI_API_KEY=your-key-here'}

# Demo Mode Settings
DEMO_MODE=${currentMode === 'demo' ? 'true' : 'false'}
`;

    fs.writeFileSync(envPath, envContent);
    return true;
});

// App event handlers
app.whenReady().then(() => {
    createSplashWindow();

    // Check for updates
    autoUpdater.checkForUpdatesAndNotify();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    isQuitting = true;
    stopPythonBackend();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createSplashWindow();
    }
});