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

const { ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');

function setupIPCHandlers(config, pythonBridge, mainWindowGetter) {
    ipcMain.handle('get-config', async () => {
        config.loadConfiguration();
        return config.getConfig();
    });

    ipcMain.handle('open-config-directory', async () => {
        try {
            const projectDir = config.getProjectDir();
            const configDir = path.join(projectDir, 'config');

            if (!fs.existsSync(configDir)) {
                config.ensureConfigFiles();
            }

            shell.openPath(configDir);
            return { success: true, path: configDir };
        } catch (error) {
            console.error('Error opening config directory:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('open-settings', async () => {
        try {
            const projectDir = config.getProjectDir();
            const settingsFile = path.join(projectDir, 'config', 'settings.yml');

            config.ensureConfigFiles();

            shell.openPath(settingsFile);
            return { success: true, path: settingsFile };
        } catch (error) {
            console.error('Error opening settings file:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('open-apps-config', async () => {
        try {
            const projectDir = config.getProjectDir();
            const appsFile = path.join(projectDir, 'config', 'loaded_apps.yml');

            config.ensureConfigFiles();

            shell.openPath(appsFile);
            return { success: true, path: appsFile };
        } catch (error) {
            console.error('Error opening apps config file:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('reload-config', async () => {
        try {
            config.reloadConfiguration();
            return { success: true, config: config.getConfig() };
        } catch (error) {
            console.error('Error reloading config:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('reloadConfig', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('reload_config');
            return result;
        } catch (error) {
            console.error('Error reloading backend config:', error);
            throw error;
        }
    });

    ipcMain.handle('updateLayoutMode', async (event, options) => {
        try {
            const { layout_mode } = options;

            const projectDir = config.getProjectDir();
            const settingsPath = path.join(projectDir, 'config', 'settings.yml');

            if (fs.existsSync(settingsPath)) {
                let settingsContent = fs.readFileSync(settingsPath, 'utf8');

                const layoutModeRegex = /(\s*layout_mode:\s*)[^\s#\n\r]+/;

                if (layoutModeRegex.test(settingsContent)) {
                    settingsContent = settingsContent.replace(layoutModeRegex, `$1${layout_mode}`);
                } else {
                    const windowRegex = /(window:\s*(?:#.*)?[\n\r])/;
                    if (windowRegex.test(settingsContent)) {
                        settingsContent = settingsContent.replace(windowRegex, `$1  layout_mode: ${layout_mode}\n`);
                    } else {
                        settingsContent = `window:\n  layout_mode: ${layout_mode}\n` + settingsContent;
                    }
                }

                fs.writeFileSync(settingsPath, settingsContent, 'utf8');

                config.reloadConfiguration();

                if (pythonBridge.getPythonProcess()) {
                    try {
                        const reloadResult = await pythonBridge.sendCommandToPython('reload_config');
                        if (!reloadResult || !reloadResult.success) {
                            console.warn('Python backend config reload failed:', reloadResult?.error || 'Unknown error');
                        }
                    } catch (reloadError) {
                        console.warn('Failed to reload Python backend config:', reloadError);
                    }
                }

                console.log('Layout mode updated and config reloaded successfully:', layout_mode);
                return { success: true, layout_mode: layout_mode };
            } else {
                throw new Error('Settings file not found');
            }
        } catch (error) {
            console.error('Error updating layout mode:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('getConfig', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('getConfig');
            return result;
        } catch (error) {
            console.error('Error getting config from backend:', error);
            config.loadConfiguration();
            return config.getConfig();
        }
    });

    ipcMain.handle('start-apps', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('start_apps');
            return result;
        } catch (error) {
            console.error('Error starting apps:', error);
            throw error;
        }
    });

    ipcMain.handle('minimize-all', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('minimize_all');
            return result;
        } catch (error) {
            console.error('Error minimizing apps:', error);
            throw error;
        }
    });

    ipcMain.handle('maximize-grid', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('maximize_grid');
            return result;
        } catch (error) {
            console.error('Error arranging windows:', error);
            throw error;
        }
    });

    ipcMain.handle('close-all', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('close_all');
            return result;
        } catch (error) {
            console.error('Error closing apps:', error);
            throw error;
        }
    });

    ipcMain.handle('reopen-all', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('reopen_all');
            return result;
        } catch (error) {
            console.error('Error reopening apps:', error);
            throw error;
        }
    });

    ipcMain.handle('get-active-apps', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('get_active_apps');
            return result;
        } catch (error) {
            console.error('Error getting active apps:', error);
            return [];
        }
    });

    ipcMain.handle('refreshAllPages', async () => {
        try {
            console.log('Sending Ctrl+R refresh to all applications...');
            const result = await pythonBridge.sendCommandToPython('refreshAllPages');
            console.log('Refresh command sent:', result);
            return result;
        } catch (error) {
            console.error('Error sending refresh command:', error);
            throw error;
        }
    });

    ipcMain.handle('bring-to-front', async (event, appName) => {
        try {
            console.log('Bringing app to front:', appName);
            const result = await pythonBridge.sendCommandToPython('bring_to_front', { appName });
            return result;
        } catch (error) {
            console.error('Error bringing app to front:', error);
            throw error;
        }
    });

    ipcMain.handle('updatePriorities', async (event, priorities) => {
        try {
            console.log('Updating priorities:', priorities);
            const result = await pythonBridge.sendCommandToPython('updatePriorities', { priorities });
            console.log('Priorities updated:', result);
            return result;
        } catch (error) {
            console.error('Error updating priorities:', error);
            throw error;
        }
    });

    ipcMain.handle('window-minimize', () => {
        const mainWindow = mainWindowGetter();
        if (mainWindow) {
            mainWindow.minimize();
        }
    });

    ipcMain.handle('window-maximize', () => {
        const mainWindow = mainWindowGetter();
        if (mainWindow) {
            if (mainWindow.isMaximized()) {
                mainWindow.unmaximize();
            } else {
                mainWindow.maximize();
            }
        }
    });

    ipcMain.handle('window-close', () => {
        const mainWindow = mainWindowGetter();
        if (mainWindow) {
            mainWindow.close();
        }
    });

    ipcMain.handle('toggle-always-on-top', () => {
        const mainWindow = mainWindowGetter();
        if (mainWindow) {
            const { Menu } = require('electron');
            const isOnTop = mainWindow.isAlwaysOnTop();
            mainWindow.setAlwaysOnTop(!isOnTop);

            const menu = Menu.getApplicationMenu();
            if (menu) {
                const viewMenu = menu.items.find(item => item.label === 'View');
                if (viewMenu) {
                    const alwaysOnTopItem = viewMenu.submenu.items.find(item => item.label === 'Always on Top');
                    if (alwaysOnTopItem) {
                        alwaysOnTopItem.checked = !isOnTop;
                    }
                }
            }

            return !isOnTop;
        }
        return false;
    });

    ipcMain.handle('getLoadAppsConfig', async () => {
        try {
            const result = await pythonBridge.sendCommandToPython('getLoadAppsConfig');
            return result;
        } catch (error) {
            console.error('Error getting load apps config from backend:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('loadSelectedProfiles', async (event, params) => {
        try {
            console.log('Loading selected profiles:', params);
            const result = await pythonBridge.sendCommandToPython('loadSelectedProfiles', params);
            console.log('Selected profiles loaded:', result);
            return result;
        } catch (error) {
            console.error('Error loading selected profiles:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('unloadProfile', async (event, params) => {
        try {
            console.log('Unloading profile:', params);
            const result = await pythonBridge.sendCommandToPython('unloadProfile', params);
            console.log('Profile unloaded:', result);
            return result;
        } catch (error) {
            console.error('Error unloading profile:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('unloadAllProfiles', async () => {
        try {
            console.log('Unloading all profiles...');
            const result = await pythonBridge.sendCommandToPython('unloadAllProfiles');
            console.log('All profiles unloaded:', result);
            return result;
        } catch (error) {
            console.error('Error unloading all profiles:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('closeSpecificApp', async (event, params) => {
        try {
            console.log('Closing specific app:', params);
            const result = await pythonBridge.sendCommandToPython('closeSpecificApp', params);
            console.log('Specific app closed:', result);
            return result;
        } catch (error) {
            console.error('Error closing specific app:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('openSpecificApp', async (event, params) => {
        try {
            console.log('Opening specific app:', params);
            const result = await pythonBridge.sendCommandToPython('openSpecificApp', params);
            console.log('Specific app opened:', result);
            return result;
        } catch (error) {
            console.error('Error opening specific app:', error);
            return { success: false, error: error.message };
        }
    });

    ipcMain.handle('open-file', async (event, filename) => {
        try {
            const projectRoot = config.getProjectDir();

            const possiblePaths = [
                path.join(projectRoot, 'config', filename),
                path.join(projectRoot, 'logs', filename),
                path.join(projectRoot, 'src', 'spectratact', filename),
                path.join(projectRoot, filename)
            ];

            let filePath = null;
            for (const testPath of possiblePaths) {
                if (fs.existsSync(testPath)) {
                    filePath = testPath;
                    break;
                }
            }

            if (!filePath) {
                console.error(`File not found: ${filename}`);
                return { success: false, error: `File not found: ${filename}` };
            }

            console.log(`Opening file: ${filePath}`);

            if (process.platform === 'win32') {
                const ext = path.extname(filePath).toLowerCase();

                if (ext === '.log' || ext === '.txt') {
                    try {
                        const { spawn } = require('child_process');
                        spawn('notepad.exe', [filePath], { detached: true, stdio: 'ignore' });
                        console.log(`File opened with Notepad: ${filePath}`);
                        return { success: true, path: filePath, method: 'notepad' };
                    } catch (notepadError) {
                        console.error('Notepad failed:', notepadError);
                        shell.showItemInFolder(filePath);
                        console.log(`File shown in Explorer: ${filePath}`);
                        return { success: true, path: filePath, method: 'explorer' };
                    }
                } else {
                    const result = await shell.openPath(filePath);
                    if (result === '') {
                        console.log(`File opened successfully: ${filePath}`);
                        return { success: true, path: filePath };
                    } else {
                        console.log(`Default app failed: ${result}, trying notepad...`);
                        try {
                            const { spawn } = require('child_process');
                            spawn('notepad.exe', [filePath], { detached: true, stdio: 'ignore' });
                            console.log(`File opened with Notepad: ${filePath}`);
                            return { success: true, path: filePath, method: 'notepad' };
                        } catch (notepadError) {
                            console.error('Notepad failed:', notepadError);
                            shell.showItemInFolder(filePath);
                            console.log(`File shown in Explorer: ${filePath}`);
                            return { success: true, path: filePath, method: 'explorer' };
                        }
                    }
                }
            } else {
                const result = await shell.openPath(filePath);
                if (result === '') {
                    console.log(`File opened successfully: ${filePath}`);
                    return { success: true, path: filePath };
                } else {
                    return { success: false, error: `Failed to open file: ${result}` };
                }
            }

        } catch (error) {
            console.error('Error opening file:', error);
            return { success: false, error: error.message };
        }
    });
}

module.exports = {
    setupIPCHandlers
};
