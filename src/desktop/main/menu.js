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

const { Menu, ipcMain, shell } = require('electron');

function createMenu(app, mainWindowGetter) {
    const template = [
        {
            label: 'File',
            submenu: [
                { type: 'separator' },
                {
                    label: 'Open Config Directory',
                    accelerator: 'CmdOrCtrl+Shift+O',
                    click: async () => {
                        const result = await ipcMain.handle('open-config-directory', {})();
                        if (result.success) {
                        }
                    }
                },
                {
                    label: 'Reload Configuration',
                    accelerator: 'CmdOrCtrl+R',
                    click: async () => {
                        const mainWindow = mainWindowGetter();
                        const result = await ipcMain.handle('reload-config', {})();
                        if (result.success) {
                            mainWindow.webContents.send('show-notification', {
                                type: 'success',
                                message: 'Configuration reloaded successfully!'
                            });
                        } else {
                            console.error('Failed to reload config:', result.error);
                            mainWindow.webContents.send('show-notification', {
                                type: 'error',
                                message: 'Failed to reload configuration: ' + result.error
                            });
                        }
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quit',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                {
                    label: 'Select All Apps',
                    accelerator: 'CmdOrCtrl+A',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'select-all-apps');
                    }
                },
                {
                    label: 'Clear Selection',
                    accelerator: 'CmdOrCtrl+D',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'clear-selection');
                    }
                },
                { type: 'separator' }
            ]
        },
        {
            label: 'Apps',
            submenu: [
                {
                    label: 'Start All Applications',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'start-apps');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Minimize All',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'minimize-all');
                    }
                },
                {
                    label: 'Arrange in Grid',
                    accelerator: 'CmdOrCtrl+G',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'arrange-grid');
                    }
                },
                {
                    label: 'Close All',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'close-all');
                    }
                }
            ]
        },
        {
            label: 'View',
            submenu: [
                {
                    label: 'Refresh Apps',
                    accelerator: 'F5',
                    click: () => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.webContents.send('menu-action', 'refresh-apps');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Always on Top',
                    type: 'checkbox',
                    checked: false,
                    click: (menuItem) => {
                        const mainWindow = mainWindowGetter();
                        mainWindow.setAlwaysOnTop(menuItem.checked);
                        mainWindow.webContents.send('menu-action', 'toggle-always-on-top', menuItem.checked);
                    }
                },
                { type: 'separator' },
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' }
            ]
        },
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'zoom' },
                ...(process.platform === 'darwin' ? [
                    { type: 'separator' },
                    { role: 'front' }
                ] : [
                    { role: 'close' }
                ])
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'About SpectraTact',
                    click: () => {
                        shell.openExternal('https://github.com/your-repo/multi-chat-manager');
                    }
                },
                {
                    label: 'Report Issue',
                    click: () => {
                        shell.openExternal('https://github.com/your-repo/multi-chat-manager/issues');
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

module.exports = {
    createMenu
};
