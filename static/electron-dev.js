/**
 * Development version of Electron main process
 * Includes additional debugging and development features
 */

const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const axios = require('axios');

class GameOverlayDevApp {
    constructor() {
        this.mainWindow = null;
        this.apiBase = 'http://127.0.0.1:8000/api/v1';
        this.devMode = true;
    }

    createWindow() {
        const { width, height } = screen.getPrimaryDisplay().workAreaSize;
        
        // Create development window with additional features
        this.mainWindow = new BrowserWindow({
            width: width,         // Full screen width
            height: height,       // Full screen height
            x: 0,                 // Start from left edge
            y: 0,                 // Start from top edge
            frame: false,
            transparent: true,
            alwaysOnTop: true,
            skipTaskbar: false,  // Show in taskbar for dev
            resizable: true,     // Allow resizing in dev
            movable: true,
            minimizable: true,
            maximizable: false,
            closable: true,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                devTools: true  // Enable dev tools in dev mode
            }
        });

        // Load the overlay HTML
        this.mainWindow.loadFile('pixly-hud.html');

        // Open dev tools automatically in development
        this.mainWindow.webContents.openDevTools();

        // Handle window events
        this.setupWindowEvents();

        // Handle IPC messages
        this.setupIPC();

        // Development-specific features
        this.setupDevFeatures();
    }

    setupWindowEvents() {
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        this.mainWindow.on('ready-to-show', () => {
            this.mainWindow.show();
        });

        // Log window events for debugging
        this.mainWindow.on('focus', () => {
            console.log('Window focused');
        });

        this.mainWindow.on('blur', () => {
            console.log('Window blurred');
        });
    }

    setupIPC() {
        // Handle API requests from renderer
        ipcMain.handle('api-request', async (event, { method, endpoint, data }) => {
            try {
                console.log(`API Request: ${method} ${endpoint}`);
                const url = `${this.apiBase}${endpoint}`;
                const response = await axios({
                    method,
                    url,
                    data,
                    timeout: 10000
                });
                console.log(`API Response: ${response.status}`);
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

        // Development-specific IPC handlers
        ipcMain.handle('get-window-info', () => {
            if (this.mainWindow) {
                const bounds = this.mainWindow.getBounds();
                return {
                    x: bounds.x,
                    y: bounds.y,
                    width: bounds.width,
                    height: bounds.height,
                    isVisible: this.mainWindow.isVisible(),
                    isFocused: this.mainWindow.isFocused()
                };
            }
            return null;
        });
    }

    setupDevFeatures() {
        // Add development menu
        this.addDevMenu();

        // Log backend connection status
        this.checkBackendConnection();

        // Add hot reload for development
        this.setupHotReload();
    }

    addDevMenu() {
        // Add development menu items
        const { Menu } = require('electron');
        
        const template = [
            {
                label: 'Development',
                submenu: [
                    {
                        label: 'Reload',
                        accelerator: 'CmdOrCtrl+R',
                        click: () => {
                            this.mainWindow.reload();
                        }
                    },
                    {
                        label: 'Toggle DevTools',
                        accelerator: 'F12',
                        click: () => {
                            this.mainWindow.webContents.toggleDevTools();
                        }
                    },
                    {
                        label: 'Check Backend',
                        click: () => {
                            this.checkBackendConnection();
                        }
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    async checkBackendConnection() {
        try {
            const response = await axios.get(`${this.apiBase}/health`, { timeout: 5000 });
            console.log('✅ Backend connection successful:', response.data);
            return true;
        } catch (error) {
            console.error('❌ Backend connection failed:', error.message);
            return false;
        }
    }

    setupHotReload() {
        // Watch for file changes and reload
        const chokidar = require('chokidar');
        
        const watcher = chokidar.watch(['index.html', 'main.js', 'preload.js'], {
            ignored: /node_modules/,
            persistent: true
        });

        watcher.on('change', (path) => {
            console.log(`File changed: ${path}`);
            this.mainWindow.reload();
        });
    }

    async start() {
        await app.whenReady();
        this.createWindow();

        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createWindow();
            }
        });

        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });
    }
}

// Create and start the development app
const overlayApp = new GameOverlayDevApp();
overlayApp.start().catch(console.error);
