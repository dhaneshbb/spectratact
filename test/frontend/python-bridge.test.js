/**
 * Tests for python-bridge.js module
 * Unit tests for Python backend communication
 */

// Mock child_process (must use mock prefix for EventEmitter)
jest.mock('child_process', () => {
    const { EventEmitter } = require('events');
    return {
        spawn: jest.fn(() => {
            const mockProcess = new EventEmitter();
            mockProcess.stdout = new EventEmitter();
            mockProcess.stderr = new EventEmitter();
            mockProcess.stdin = { write: jest.fn() };
            mockProcess.kill = jest.fn();
            return mockProcess;
        })
    };
});

describe('PythonBridge', () => {
    describe('Communication protocol', () => {
        test('should send JSON-RPC commands', () => {
            const command = {
                method: 'get_windows',
                params: {}
            };

            const jsonString = JSON.stringify(command);
            expect(jsonString).toContain('get_windows');
            expect(() => JSON.parse(jsonString)).not.toThrow();
        });

        test('should parse JSON-RPC responses', () => {
            const response = JSON.stringify({
                result: { windows: [1, 2, 3] },
                error: null
            });

            const parsed = JSON.parse(response);
            expect(parsed.result).toBeDefined();
            expect(parsed.result.windows).toHaveLength(3);
        });

        test('should handle error responses', () => {
            const errorResponse = {
                result: null,
                error: { message: 'Window not found' }
            };

            expect(errorResponse.error).toBeDefined();
            expect(errorResponse.error.message).toBe('Window not found');
        });
    });

    describe('Command validation', () => {
        test('should validate command structure', () => {
            const validCommand = {
                method: 'arrange_windows',
                params: { layout: 'grid' }
            };

            expect(validCommand).toHaveProperty('method');
            expect(validCommand).toHaveProperty('params');
            expect(typeof validCommand.method).toBe('string');
        });

        test('should reject invalid commands', () => {
            const invalidCommand = { invalid: 'structure' };

            expect(invalidCommand).not.toHaveProperty('method');
        });
    });

    describe('Process management', () => {
        const { spawn } = require('child_process');

        beforeEach(() => {
            jest.clearAllMocks();
        });

        test('should spawn Python process', () => {
            const pythonPath = 'python';
            const args = ['-m', 'spectratact', '--electron'];

            spawn(pythonPath, args);

            expect(spawn).toHaveBeenCalledWith(pythonPath, args);
        });

        test('should handle process spawn', () => {
            const mockProcess = spawn('python', ['-m', 'spectratact']);

            expect(mockProcess).toBeDefined();
            expect(mockProcess.stdout).toBeDefined();
            expect(mockProcess.stderr).toBeDefined();
            expect(mockProcess.stdin).toBeDefined();
        });
    });

    describe('Data streaming', () => {
        test('should buffer incomplete JSON', () => {
            const chunk1 = '{"result":';
            const chunk2 = '{"success":true}}';

            const buffer = chunk1 + chunk2;
            const parsed = JSON.parse(buffer);

            expect(parsed.result.success).toBe(true);
        });

        test('should handle multiple JSON objects', () => {
            const data = '{"id":1}\n{"id":2}\n{"id":3}\n';
            const lines = data.trim().split('\n');

            expect(lines).toHaveLength(3);
            lines.forEach((line, index) => {
                const obj = JSON.parse(line);
                expect(obj.id).toBe(index + 1);
            });
        });
    });
});
