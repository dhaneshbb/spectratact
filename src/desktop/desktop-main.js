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

const { app, BrowserWindow } = require('electron');
const path = require('path');

const { createWindow, getMainWindow } = require('./main/window');
const { startPythonBackend, stopPythonBackend, setAppConfig } = require('./main/python-bridge');
const { loadConfiguration, getProjectDir, setPythonBridge, setMainWindow, setReloadCallback, reloadConfiguration, stopWatchers } = require('./main/config');
const { setupIPCHandlers } = require('./main/ipc-handlers');
const { createMenu } = require('./main/menu');
const pythonBridge = require('./main/python-bridge');
const config = require('./main/config');

if (process.env.NODE_ENV === 'development') {
    try {
        require('electron-reload')(__dirname, {
            electron: path.join(__dirname, '..', '..', 'node_modules', '.bin', 'electron'),
            hardResetMethod: 'exit'
        });
    } catch (e) {
    }
}

const packageJson = require('../../package.json');
app.setName('SpectraTact');
app.setVersion(packageJson.version);

app.whenReady().then(() => {
    const appConfig = loadConfiguration();
    setAppConfig(appConfig);

    setPythonBridge(pythonBridge);
    setMainWindow(getMainWindow);
    setReloadCallback(reloadConfiguration);

    setupIPCHandlers(config, pythonBridge, getMainWindow);

    const pythonBackendStarter = {
        start: () => startPythonBackend(getProjectDir),
        stop: stopPythonBackend
    };

    const menuCreator = () => createMenu(app, getMainWindow);

    createWindow(appConfig, pythonBackendStarter, menuCreator);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow(appConfig, pythonBackendStarter, menuCreator);
        }
    });
});

app.on('window-all-closed', () => {
    stopPythonBackend();
    stopWatchers();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('web-contents-created', (event, contents) => {
    contents.on('new-window', (navigationEvent, navigationURL) => {
        navigationEvent.preventDefault();
        const { shell } = require('electron');
        shell.openExternal(navigationURL);
    });
});

app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
    if (process.env.NODE_ENV === 'development') {
        event.preventDefault();
        callback(true);
    } else {
        callback(false);
    }
});

app.on('web-contents-created', (event, contents) => {
    contents.on('will-navigate', (navigationEvent, navigationURL) => {
        const parsedUrl = new URL(navigationURL);

        if (parsedUrl.origin !== 'null') {
            navigationEvent.preventDefault();
        }
    });
});

app.setAsDefaultProtocolClient('multi-chat');

const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        const mainWindow = getMainWindow();
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.focus();
        }
    });
}

console.log('Desktop SpectraTact starting...');
