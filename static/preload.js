/**
 * Electron preload script for Game Overlay AI
 * Provides secure communication between main and renderer processes
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // API request handler
    apiRequest: (method, endpoint, data) => {
        return ipcRenderer.invoke('api-request', { method, endpoint, data });
    },

    // Window control
    minimizeWindow: () => {
        return ipcRenderer.invoke('minimize-window');
    },

    closeWindow: () => {
        return ipcRenderer.invoke('close-window');
    },

    // Overlay positioning
    setPosition: (x, y) => {
        return ipcRenderer.invoke('set-position', { x, y });
    },

    setSize: (width, height) => {
        return ipcRenderer.invoke('set-size', { width, height });
    },

    // Event listeners
    on: (channel, callback) => {
        const validChannels = ['window-focus', 'window-blur'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, callback);
        }
    },

    removeAllListeners: (channel) => {
        const validChannels = ['window-focus', 'window-blur'];
        if (validChannels.includes(channel)) {
            ipcRenderer.removeAllListeners(channel);
        }
    }
});
