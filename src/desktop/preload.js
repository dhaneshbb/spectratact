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

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Configuration
    getConfig: () => ipcRenderer.invoke('getConfig'),
    reloadConfig: () => ipcRenderer.invoke('reload-config'),
    updateLayoutMode: (options) => ipcRenderer.invoke('updateLayoutMode', options),

    // App Management
    startApps: () => ipcRenderer.invoke('start-apps'),
    refreshAllPages: () => ipcRenderer.invoke('refreshAllPages'),
    minimizeAll: () => ipcRenderer.invoke('minimize-all'),
    maximizeGrid: () => ipcRenderer.invoke('maximize-grid'),
    closeAll: () => ipcRenderer.invoke('close-all'),
    reopenAll: () => ipcRenderer.invoke('reopen-all'),
    getActiveApps: () => ipcRenderer.invoke('get-active-apps'),
    bringToFront: (appName) => ipcRenderer.invoke('bring-to-front', appName),

    // Window Controls
    windowMinimize: () => ipcRenderer.invoke('window-minimize'),
    windowMaximize: () => ipcRenderer.invoke('window-maximize'),
    windowClose: () => ipcRenderer.invoke('window-close'),
    toggleAlwaysOnTop: () => ipcRenderer.invoke('toggle-always-on-top'),

    // File Operations
    openFile: (filename) => ipcRenderer.invoke('open-file', filename),
    openConfigDirectory: () => ipcRenderer.invoke('open-config-directory'),

    // Onboarding (Config File Operations)
    openSettings: () => ipcRenderer.invoke('open-settings'),
    openAppsConfig: () => ipcRenderer.invoke('open-apps-config'),

    // Priority Management
    updatePriorities: (priorities) => ipcRenderer.invoke('updatePriorities', priorities),

    // Load Apps Management
    getLoadAppsConfig: () => ipcRenderer.invoke('getLoadAppsConfig'),
    loadSelectedProfiles: (params) => ipcRenderer.invoke('loadSelectedProfiles', params),
    unloadProfile: (params) => ipcRenderer.invoke('unloadProfile', params),
    unloadAllProfiles: () => ipcRenderer.invoke('unloadAllProfiles'),
    closeSpecificApp: (params) => ipcRenderer.invoke('closeSpecificApp', params),
    openSpecificApp: (params) => ipcRenderer.invoke('openSpecificApp', params),


    // Events
    onMenuClick: (callback) => ipcRenderer.on('menu-click', callback),
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});
