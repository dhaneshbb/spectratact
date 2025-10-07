/**
 * Jest configuration for frontend testing
 */

module.exports = {
    testEnvironment: 'node',
    testMatch: [
        '<rootDir>/test/frontend/**/*.test.js',
        '<rootDir>/test/frontend/**/*.spec.js'
    ],
    collectCoverageFrom: [
        'src/desktop/main/**/*.js',
        'src/desktop/desktop-app.js',
        '!**/node_modules/**'
    ],
    coverageDirectory: 'coverage/frontend',
    coverageReporters: ['text', 'lcov', 'html'],
    roots: ['<rootDir>/test/frontend'],
    moduleDirectories: ['node_modules', 'src/desktop', 'src/desktop/node_modules'],
    moduleNameMapper: {
        '^electron$': '<rootDir>/test/frontend/__mocks__/electron.js'
    },
};
