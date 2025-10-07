/**
 * SpectraTact - Desktop Application Management
 * Copyright (c) 2025 dhaneshbb
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

const { BrowserWindow } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow(config, pythonBackendStarter, menuCreator) {
    if (!config?.gui?.window) {
        console.error('CRITICAL ERROR: Missing gui.window configuration in settings.yml');
        process.exit(1);
    }

    const windowConfig = config.gui.window;
    if (!windowConfig.width || !windowConfig.height) {
        console.error('CRITICAL ERROR: Missing width/height in gui.window configuration');
        process.exit(1);
    }

    const width = windowConfig.width;
    const height = windowConfig.height;
    const alwaysOnTop = windowConfig.always_on_top || false;

    mainWindow = new BrowserWindow({
        width: width,
        height: height,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, '..', 'preload.js'),
            webSecurity: true
        },
        frame: false,
        backgroundColor: '#202020',
        show: false,
        titleBarStyle: 'hiddenInset',
        icon: path.join(__dirname, '..', 'assets', 'icons', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
        vibrancy: 'dark',
        backgroundMaterial: 'acrylic'
    });

    mainWindow.loadFile(path.join(__dirname, '..', 'desktop-index.html'));

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        mainWindow.setAlwaysOnTop(alwaysOnTop);

        if (process.platform === 'darwin') {
            mainWindow.focus();
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
        if (pythonBackendStarter && pythonBackendStarter.stop) {
            pythonBackendStarter.stop();
        }
    });

    mainWindow.on('maximize', () => {
        mainWindow.webContents.send('window-maximized');
    });

    mainWindow.on('unmaximize', () => {
        mainWindow.webContents.send('window-unmaximized');
    });

    if (process.argv.includes('--dev') || process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }

    if (menuCreator) {
        menuCreator();
    }

    if (pythonBackendStarter && pythonBackendStarter.start) {
        pythonBackendStarter.start();
    }

    return mainWindow;
}

function getMainWindow() {
    return mainWindow;
}

module.exports = {
    createWindow,
    getMainWindow
};
