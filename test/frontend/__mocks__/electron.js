/**
 * Mock Electron module for testing
 */

module.exports = {
    app: {
        getPath: jest.fn(() => '/mock/config/path'),
        on: jest.fn(),
        quit: jest.fn()
    },
    BrowserWindow: jest.fn().mockImplementation(() => ({
        loadFile: jest.fn(),
        webContents: {
            openDevTools: jest.fn(),
            send: jest.fn()
        },
        on: jest.fn(),
        isMinimized: jest.fn(() => false),
        restore: jest.fn(),
        show: jest.fn(),
        focus: jest.fn()
    })),
    ipcMain: {
        on: jest.fn(),
        handle: jest.fn()
    },
    screen: {
        getPrimaryDisplay: jest.fn(() => ({
            workAreaSize: { width: 1920, height: 1080 }
        })),
        getAllDisplays: jest.fn(() => [
            { workAreaSize: { width: 1920, height: 1080 } }
        ])
    },
    Menu: {
        buildFromTemplate: jest.fn(),
        setApplicationMenu: jest.fn()
    }
};
