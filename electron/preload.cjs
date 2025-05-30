const { contextBridge, ipcRenderer } = require('electron');

// Safe API to expose to the renderer process
contextBridge.exposeInMainWorld('api', {
    send: (channel, data) => {
        // Whitelist of channels for sending data from renderer to main process
        const validChannels = ['toMain'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    receive: (channel, func) => {
        // Whitelist of channels for receiving data from main to renderer process
        const validChannels = ['fromMain'];
        if (validChannels.includes(channel)) {
            // Remove all listeners from the channel before adding a new one
            // This prevents multiple listeners from being registered
            ipcRenderer.removeAllListeners(channel);
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    }
});