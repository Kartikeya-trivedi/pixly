/**
 * Electron main process for Game Overlay AI
 * Creates transparent, always-on-top overlay window
 */

const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const axios = require('axios');

class GameOverlayApp {
    constructor() {
        this.mainWindow = null;
        this.isDev = process.argv.includes('--dev');
        this.apiBase = 'http://127.0.0.1:8000/api/v1';
    }

    createWindow() {
        const { width, height } = screen.getPrimaryDisplay().workAreaSize;
        
        // Create transparent, always-on-top window
        this.mainWindow = new BrowserWindow({
            width: width,         // Full screen width
            height: height,       // Full screen height
            x: 0,                 // Start from left edge
            y: 0,                 // Start from top edge
            frame: false,                    // No window frame
            transparent: true,              // Transparent background
            alwaysOnTop: true,              // Always on top
            skipTaskbar: true,              // Don't show in taskbar
            resizable: false,               // Fixed size
            movable: true,                  // Allow dragging
            minimizable: false,             // No minimize button
            maximizable: false,             // No maximize button
            closable: true,                 // Allow closing
            webPreferences: {
                nodeIntegration: false,     // Security: no node integration
                contextIsolation: true,    // Security: context isolation
                enableRemoteModule: false,  // Security: no remote module
                preload: path.join(__dirname, 'preload.js')
            }
        });

        // Load the overlay HTML
        this.mainWindow.loadFile('pixly-hud.html');

        // Handle window events
        this.setupWindowEvents();

        // Handle IPC messages
        this.setupIPC();

        // Development tools
        if (this.isDev) {
            this.mainWindow.webContents.openDevTools();
        }
    }

    setupWindowEvents() {
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // Prevent window from being closed accidentally
        this.mainWindow.on('close', (event) => {
            if (!this.isDev) {
                event.preventDefault();
                this.mainWindow.hide();
            }
        });

        // Handle window dragging
        this.mainWindow.on('ready-to-show', () => {
            this.mainWindow.show();
        });
    }

    setupIPC() {
        // Handle API requests from renderer
        ipcMain.handle('api-request', async (event, { method, endpoint, data }) => {
            try {
                const url = `${this.apiBase}${endpoint}`;
                const response = await axios({
                    method,
                    url,
                    data,
                    timeout: 10000
                });
                return { success: true, data: response.data };
            } catch (error) {
                console.error('API request failed:', error);
                return { 
                    success: false, 
                    error: error.message,
                    status: error.response?.status 
                };
            }
        });

        // Handle window control
        ipcMain.handle('minimize-window', () => {
            if (this.mainWindow) {
                this.mainWindow.minimize();
            }
        });

        ipcMain.handle('close-window', () => {
            if (this.mainWindow) {
                this.mainWindow.close();
            }
        });

        // Handle overlay positioning
        ipcMain.handle('set-position', (event, { x, y }) => {
            if (this.mainWindow) {
                this.mainWindow.setPosition(x, y);
            }
        });

        // Handle overlay size
        ipcMain.handle('set-size', (event, { width, height }) => {
            if (this.mainWindow) {
                this.mainWindow.setSize(width, height);
            }
        });
    }

    async checkBackendConnection() {
        try {
            const response = await axios.get(`${this.apiBase}/health`, { timeout: 5000 });
            console.log('Backend connection successful:', response.data);
            return true;
        } catch (error) {
            console.error('Backend connection failed:', error.message);
            return false;
        }
    }

    async start() {
        // Wait for app to be ready
        await app.whenReady();

        // Check backend connection
        const backendConnected = await this.checkBackendConnection();
        if (!backendConnected) {
            console.warn('Backend not available. Some features may not work.');
        }

        // Create the overlay window
        this.createWindow();

        // Handle app activation (macOS)
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createWindow();
            }
        });

        // Handle app window-all-closed
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });
    }
}

// Create and start the app
const overlayApp = new GameOverlayApp();
overlayApp.start().catch(console.error);

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
