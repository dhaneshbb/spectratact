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

const path = require('path');
const fs = require('fs');
const yaml = require('js-yaml');

let appConfig = null;
let configWatchers = [];

function getProjectDir() {
    const { app } = require('electron');
    const isPackaged = app.isPackaged;

    if (isPackaged) {
        return process.resourcesPath;
    } else {
        return path.join(__dirname, '..', '..', '..');
    }
}

function ensureConfigFiles() {
    const projectDir = getProjectDir();
    const configDir = path.join(projectDir, 'config');

    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
    }

    const configFiles = ['settings.yml', 'loaded_apps.yml'];

    configFiles.forEach((name) => {
        const configPath = path.join(configDir, name);
        if (!fs.existsSync(configPath)) {
            const examplePath = path.join(projectDir, 'example', `${name}.example`);
            if (fs.existsSync(examplePath)) {
                try {
                    fs.copyFileSync(examplePath, configPath);
                } catch (error) {
                    console.error(`Error copying ${examplePath} to ${configPath}:`, error);
                }
            }
        }
    });
}

function loadConfiguration() {
    const projectDir = getProjectDir();

    ensureConfigFiles();

    const settingsPath = path.join(projectDir, 'config', 'settings.yml');
    const appsPath = path.join(projectDir, 'config', 'loaded_apps.yml');

    let settingsConfig = null;
    if (fs.existsSync(settingsPath)) {
        try {
            const configFile = fs.readFileSync(settingsPath, 'utf8');
            settingsConfig = yaml.load(configFile);
        } catch (error) {
            console.error('Error loading settings from', settingsPath, ':', error);
            process.exit(1);
        }
    } else {
        console.error('CRITICAL ERROR: No settings.yml found at:', settingsPath);
        process.exit(1);
    }

    let appsConfig = null;
    if (fs.existsSync(appsPath)) {
        try {
            const configFile = fs.readFileSync(appsPath, 'utf8');
            appsConfig = yaml.load(configFile);
        } catch (error) {
            console.error('Error loading apps from', appsPath, ':', error);
            process.exit(1);
        }
    } else {
        console.error('CRITICAL ERROR: No loaded_apps.yml found at:', appsPath);
        process.exit(1);
    }

    appConfig = { ...settingsConfig };
    appConfig.apps = appsConfig.apps;

    setupConfigWatchers();

    return appConfig;
}

function setupConfigWatchers() {
    configWatchers.forEach(watcher => {
        watcher.close();
    });
    configWatchers = [];

    const projectDir = getProjectDir();
    const watchPaths = [
        path.join(projectDir, 'config', 'settings.yml'),
        path.join(projectDir, 'config', 'loaded_apps.yml')
    ];

    watchPaths.forEach(configPath => {
        if (fs.existsSync(configPath)) {
            try {
                fs.watchFile(configPath, { interval: 1000 }, () => {
                    if (reloadConfigurationCallback) {
                        reloadConfigurationCallback();
                    }
                });
                configWatchers.push({ close: () => fs.unwatchFile(configPath) });
            } catch (error) {
                console.error(`Error watching config file ${configPath}:`, error);
            }
        }
    });
}

let reloadConfigurationCallback = null;
let pythonBridgeRef = null;
let mainWindowRef = null;

function setReloadCallback(callback) {
    reloadConfigurationCallback = callback;
}

function setPythonBridge(bridge) {
    pythonBridgeRef = bridge;
}

function setMainWindow(windowGetter) {
    mainWindowRef = windowGetter;
}

function reloadConfiguration() {
    let oldConfig = null;
    try {
        oldConfig = appConfig;
        appConfig = null;

        loadConfiguration();

        if (pythonBridgeRef && pythonBridgeRef.getPythonProcess && pythonBridgeRef.getPythonProcess()) {
            pythonBridgeRef.sendCommandToPython('reload_config')
                .then((result) => {
                    if (result.success) {
                    } else {
                        console.error('Python backend configuration reload failed:', result.error);
                    }
                })
                .catch((error) => {
                    console.error('Error reloading Python backend configuration:', error);
                });
        }

        const mainWindow = mainWindowRef ? mainWindowRef() : null;
        if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('config-reloaded', appConfig);
        }

        if (pythonBridgeRef && pythonBridgeRef.getPythonProcess && pythonBridgeRef.getPythonProcess()) {
            pythonBridgeRef.sendCommandToPython('maximize_grid')
                .then((result) => {
                    if (result.success) {
                    }
                })
                .catch((error) => {
                    console.error('Error auto-arranging windows:', error);
                });
        }
    } catch (error) {
        console.error('Error reloading configuration:', error);
        if (oldConfig) {
            appConfig = oldConfig;
        }
    }
}

function getConfig() {
    return appConfig;
}

function stopWatchers() {
    configWatchers.forEach(watcher => {
        watcher.close();
    });
    configWatchers = [];
}

module.exports = {
    loadConfiguration,
    getProjectDir,
    getConfig,
    ensureConfigFiles,
    setupConfigWatchers,
    setReloadCallback,
    setPythonBridge,
    setMainWindow,
    reloadConfiguration,
    stopWatchers
};
