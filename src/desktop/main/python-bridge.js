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

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let pythonProcess = null;
let commandQueue = [];
let isProcessingCommands = false;
let responseCache = new Map();
let appConfig = null;

function setAppConfig(config) {
    appConfig = config;
}

function startPythonBackend(getProjectDir) {
    try {
        const { app } = require('electron');
        const projectRoot = getProjectDir();

        const isDevelopment = process.argv.includes('--dev') || process.env.NODE_ENV === 'development';
        const isPackaged = app.isPackaged;

        let pythonPath;
        let workingDir;

        if (isPackaged) {
            const resourcesPath = process.resourcesPath;
            pythonPath = path.join(resourcesPath, 'spectratact');
            workingDir = resourcesPath;
            console.log('Production mode - Resources path:', resourcesPath);
            console.log('Python module path:', pythonPath);
        } else {
            pythonPath = path.join(projectRoot, 'src');
            workingDir = projectRoot;
            console.log('Development mode - Project root:', projectRoot);
            console.log('Python module path:', pythonPath);
        }

        if (!fs.existsSync(pythonPath)) {
            const error = `Python module not found at: ${pythonPath}`;
            console.error(error);
            const { dialog } = require('electron');
            dialog.showErrorBox('Python Module Missing', error);
            return;
        }

        const pythonExecutables = ['python', 'py'];
        let pythonExe = null;
        let pythonVersion = null;

        for (const exe of pythonExecutables) {
            try {
                const testProcess = require('child_process').spawnSync(exe, ['--version'], {
                    encoding: 'utf8',
                    windowsHide: true
                });
                if (testProcess.status === 0) {
                    const versionOutput = testProcess.stdout || testProcess.stderr;
                    const versionMatch = versionOutput.match(/Python (\d+)\.(\d+)\.(\d+)/);

                    if (versionMatch) {
                        const major = parseInt(versionMatch[1]);
                        const minor = parseInt(versionMatch[2]);

                        if (major === 3 && minor >= 8) {
                            pythonExe = exe;
                            pythonVersion = versionOutput.trim();
                            console.log(`Found compatible Python: ${exe} - ${pythonVersion}`);
                            break;
                        } else {
                            console.warn(`Found ${exe} but version ${major}.${minor} is too old (need 3.8+)`);
                        }
                    }
                }
            } catch (error) {
                continue;
            }
        }

        if (!pythonExe) {
            const error = 'Python 3.8+ not found in PATH';
            console.error(error);
            const { dialog } = require('electron');
            dialog.showErrorBox(
                'Python Not Found',
                `Python 3.8+ is required.\n\nInstall from: https://www.python.org/downloads/\n\nMake sure "Add Python to PATH" is checked during installation.\n\nAfter installing Python, run setup_python.bat in the installation folder to install dependencies.`
            );
            return;
        }

        pythonProcess = spawn(pythonExe, ['-m', 'spectratact.main', '--electron'], {
            cwd: workingDir,
            stdio: ['pipe', 'pipe', 'pipe'],
            windowsHide: true,
            encoding: 'utf8',
            env: {
                ...process.env,
                PYTHONPATH: pythonPath,
                PROJECT_ROOT: workingDir,
                PATH: process.env.PATH,
                PYTHONIOENCODING: 'utf-8'
            }
        });

        pythonProcess.stdout.on('data', (data) => {
            const str = data.toString().trim();
            if (str.includes('ERROR') || str.includes('CRITICAL') || (str.includes('WARNING') && str.length > 10)) {
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            const str = data.toString().trim();
            console.error(`Python stderr: ${str}`);
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python process exited with code ${code}`);
            pythonProcess = null;
            commandQueue.forEach(cmd => cmd.reject(new Error('Python process closed')));
            commandQueue = [];
            isProcessingCommands = false;
        });

        pythonProcess.on('error', (error) => {
            console.error('Failed to start Python process:', error);
            pythonProcess = null;
            commandQueue.forEach(cmd => {
                if (cmd.reject) cmd.reject(new Error('Python process failed to start'));
            });
            commandQueue = [];
            isProcessingCommands = false;

            const { dialog } = require('electron');
            dialog.showErrorBox(
                'Python Backend Error',
                `Failed to start Python backend.\n\nError: ${error.message}\n\nPlease ensure:\n1. Python 3.8+ is installed\n2. Python is in your PATH\n3. Required dependencies are installed:\n   pip install -r requirements.txt`
            );
        });

        setTimeout(() => {
            if (pythonProcess && pythonProcess.pid) {
                console.log('Python backend ready with PID:', pythonProcess.pid);
            } else {
                console.error('Python backend failed to start properly');
            }
        }, 2000);

    } catch (error) {
        console.error('Error starting Python backend:', error);
    }
}

function stopPythonBackend() {
    if (pythonProcess) {
        pythonProcess.kill();
        pythonProcess = null;
        console.log('Python backend stopped');
    }
}

function sendCommandToPython(method, params = {}) {
    return new Promise((resolve, reject) => {
        if (!pythonProcess) {
            console.log('Python backend not running, attempting to restart...');
            reject(new Error('Python backend not running'));
            return;
        }

        const CACHE_TTL = appConfig?.communication?.cache_ttl || 1000;
        const cacheKey = method + (params ? JSON.stringify(params) : '');

        if (method === 'get_active_apps' || method === 'getConfig') {
            const cached = responseCache.get(cacheKey);
            if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
                resolve(cached.data);
                return;
            }
        }

        const command = {
            method: method,
            params: params,
            resolve: resolve,
            reject: reject,
            timestamp: Date.now(),
            cacheKey: cacheKey
        };

        commandQueue.push(command);
        processCommandQueue();
    });
}

function processCommandQueue() {
    if (isProcessingCommands || commandQueue.length === 0 || !pythonProcess) {
        return;
    }

    isProcessingCommands = true;
    const command = commandQueue.shift();

    const commandJson = JSON.stringify({
        method: command.method,
        params: command.params
    }) + '\n';

    const commandBuffer = Buffer.from(commandJson, 'utf8');

    let responseBuffer = '';

    const responseHandler = (data) => {
        responseBuffer += data.toString();

        let newlineIndex = responseBuffer.indexOf('\n');
        if (newlineIndex !== -1) {
            const line = responseBuffer.substring(0, newlineIndex).trim();
            if (line) {
                try {
                    const response = JSON.parse(line);
                    if (pythonProcess && pythonProcess.stdout) {
                        pythonProcess.stdout.removeListener('data', responseHandler);
                    }
                    clearTimeout(timeoutId);

                    if (command.cacheKey && (command.method === 'get_active_apps' || command.method === 'getConfig')) {
                        responseCache.set(command.cacheKey, {
                            data: response,
                            timestamp: Date.now()
                        });

                        if (responseCache.size > 15) {
                            const entries = Array.from(responseCache.entries());
                            responseCache.clear();
                            entries.slice(-10).forEach(([key, value]) => {
                                responseCache.set(key, value);
                            });
                        }
                    }

                    command.resolve(response);
                    isProcessingCommands = false;

                    setTimeout(processCommandQueue, 0);
                    return;
                } catch (error) {
                    console.warn('Failed to parse JSON response:', error.message);
                }
            }
            responseBuffer = responseBuffer.substring(newlineIndex + 1);
        }
    };

    pythonProcess.stdout.on('data', responseHandler);

    try {
        pythonProcess.stdin.write(commandBuffer);
    } catch (error) {
        console.error('Error writing to Python process:', error);
        command.reject(new Error('Failed to send command to Python backend'));
        isProcessingCommands = false;
        setImmediate(processCommandQueue);
        return;
    }

    const timeouts = appConfig?.communication?.timeouts || {
        default: 8000,
        start_apps: 25000,
        refresh_all_pages: 15000
    };

    const timeout = (() => {
        switch (command.method) {
            case 'start_apps': return timeouts.start_apps;
            case 'refresh_all_pages': return timeouts.refresh_all_pages || 15000;
            default: return timeouts.default;
        }
    })();

    const timeoutId = setTimeout(() => {
        if (pythonProcess && pythonProcess.stdout) {
            pythonProcess.stdout.removeListener('data', responseHandler);
        }
        command.reject(new Error('Python backend timeout'));
        isProcessingCommands = false;
        setImmediate(processCommandQueue);
    }, timeout);
}

function getPythonProcess() {
    return pythonProcess;
}

module.exports = {
    startPythonBackend,
    stopPythonBackend,
    sendCommandToPython,
    getPythonProcess,
    setAppConfig
};
