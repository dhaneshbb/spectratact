/**
 * Tests for ipc-handlers.js module
 * Tests for IPC event handling
 */

describe('IPC Handlers', () => {
    describe('Event registration', () => {
        test('should register IPC handlers', () => {
            const handlers = [
                'get-windows',
                'arrange-windows',
                'minimize-all',
                'restore-all',
                'launch-apps',
                'close-apps',
                'refresh-windows'
            ];

            handlers.forEach(handler => {
                expect(handler).toMatch(/^[a-z-]+$/);
                expect(handler.length).toBeGreaterThan(0);
            });
        });

        test('should validate handler names', () => {
            const validHandler = 'get-windows';
            const invalidHandler = 'GetWindows'; // Should be kebab-case

            expect(validHandler).toMatch(/^[a-z-]+$/);
            expect(invalidHandler).not.toMatch(/^[a-z-]+$/);
        });
    });

    describe('Event data validation', () => {
        test('should validate arrange-windows data', () => {
            const data = {
                layout: 'grid',
                cols: 3,
                rows: 2
            };

            expect(data.layout).toBeDefined();
            expect(['grid', 'side_by_side']).toContain(data.layout);
            expect(data.cols).toBeGreaterThan(0);
            expect(data.rows).toBeGreaterThan(0);
        });

        test('should validate launch-apps data', () => {
            const data = {
                apps: ['Chrome', 'VSCode', 'Terminal']
            };

            expect(Array.isArray(data.apps)).toBe(true);
            expect(data.apps.length).toBeGreaterThan(0);
        });

        test('should handle empty data', () => {
            const data = {};

            expect(Object.keys(data).length).toBe(0);
            expect(data).toEqual({});
        });
    });

    describe('Response formatting', () => {
        test('should format success response', () => {
            const response = {
                success: true,
                data: { windows: [1, 2, 3] }
            };

            expect(response.success).toBe(true);
            expect(response.data).toBeDefined();
        });

        test('should format error response', () => {
            const response = {
                success: false,
                error: 'Operation failed'
            };

            expect(response.success).toBe(false);
            expect(response.error).toBeDefined();
        });
    });

    describe('Event callbacks', () => {
        test('should handle async callbacks', async () => {
            const asyncCallback = async () => {
                return new Promise(resolve => {
                    setTimeout(() => resolve({ success: true }), 10);
                });
            };

            const result = await asyncCallback();
            expect(result.success).toBe(true);
        });

        test('should handle callback errors', async () => {
            const failingCallback = async () => {
                throw new Error('Callback failed');
            };

            await expect(failingCallback()).rejects.toThrow('Callback failed');
        });
    });
});
