const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Backend control
    startBackend: () => ipcRenderer.invoke('start-backend'),
    stopBackend: () => ipcRenderer.invoke('stop-backend'),

    // Window controls
    minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
    maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
    closeWindow: () => ipcRenderer.invoke('close-window'),

    // Flask interface
    openFlask: () => ipcRenderer.invoke('open-flask'),

    // Terminal output
    onTerminalOutput: (callback) => {
        ipcRenderer.on('terminal-output', (event, data) => callback(data));
    },

    // Backend status
    onBackendStatus: (callback) => {
        ipcRenderer.on('backend-status', (event, status) => callback(status));
    },

    // Remove listeners
    removeAllListeners: () => {
        ipcRenderer.removeAllListeners('terminal-output');
        ipcRenderer.removeAllListeners('backend-status');
    }
});