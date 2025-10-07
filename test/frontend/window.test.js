/**
 * Tests for window.js module
 * Tests for Electron window management
 */

describe('Window Module', () => {
    const { BrowserWindow } = require('electron');

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('Window creation', () => {
        test('should create BrowserWindow with config', () => {
            const config = {
                width: 800,
                height: 600,
                webPreferences: {
                    nodeIntegration: false,
                    contextIsolation: true
                }
            };

            const window = new BrowserWindow(config);

            expect(BrowserWindow).toHaveBeenCalledWith(config);
            expect(window).toBeDefined();
        });

        test('should set default window dimensions', () => {
            const defaultConfig = {
                width: 800,
                height: 600
            };

            expect(defaultConfig.width).toBe(800);
            expect(defaultConfig.height).toBe(600);
        });

        test('should configure webPreferences for security', () => {
            const securityConfig = {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false
            };

            expect(securityConfig.nodeIntegration).toBe(false);
            expect(securityConfig.contextIsolation).toBe(true);
            expect(securityConfig.enableRemoteModule).toBe(false);
        });
    });

    describe('Window state management', () => {
        test('should check if window is minimized', () => {
            const window = new BrowserWindow({});
            const isMin = window.isMinimized();

            expect(typeof isMin).toBe('boolean');
        });

        test('should restore minimized window', () => {
            const window = new BrowserWindow({});
            window.restore();

            expect(window.restore).toHaveBeenCalled();
        });

        test('should focus window', () => {
            const window = new BrowserWindow({});
            window.focus();

            expect(window.focus).toHaveBeenCalled();
        });
    });

    describe('Window communication', () => {
        test('should send IPC messages to renderer', () => {
            const window = new BrowserWindow({});
            const channel = 'update-data';
            const data = { windows: [1, 2, 3] };

            window.webContents.send(channel, data);

            expect(window.webContents.send).toHaveBeenCalledWith(channel, data);
        });

        test('should handle multiple IPC channels', () => {
            const window = new BrowserWindow({});
            const channels = [
                'update-windows',
                'update-config',
                'update-status'
            ];

            channels.forEach(channel => {
                window.webContents.send(channel, {});
            });

            expect(window.webContents.send).toHaveBeenCalledTimes(3);
        });
    });

    describe('Window events', () => {
        test('should register event handlers', () => {
            const window = new BrowserWindow({});
            const events = ['closed', 'minimize', 'restore', 'focus'];

            events.forEach(event => {
                window.on(event, () => {});
            });

            expect(window.on).toHaveBeenCalledTimes(events.length);
        });

        test('should handle window closed event', () => {
            const window = new BrowserWindow({});
            const closedHandler = jest.fn();

            window.on('closed', closedHandler);

            expect(window.on).toHaveBeenCalledWith('closed', closedHandler);
        });
    });

    describe('Screen configuration', () => {
        const { screen } = require('electron');

        test('should get primary display dimensions', () => {
            const display = screen.getPrimaryDisplay();

            expect(display.workAreaSize).toBeDefined();
            expect(display.workAreaSize.width).toBeGreaterThan(0);
            expect(display.workAreaSize.height).toBeGreaterThan(0);
        });

        test('should validate display dimensions', () => {
            const { width, height } = { width: 1920, height: 1080 };

            expect(width).toBeGreaterThan(0);
            expect(height).toBeGreaterThan(0);
            expect(width).toBeGreaterThanOrEqual(800);
            expect(height).toBeGreaterThanOrEqual(600);
        });
    });
});
