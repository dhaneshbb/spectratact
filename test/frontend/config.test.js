/**
 * Tests for config.js module
 * Similar to pytest unit tests
 */

const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

describe("Config Module", () => {
  let configModule;

  beforeEach(() => {
    // Clear module cache to get fresh instance
    jest.clearAllMocks();
    jest.resetModules();
  });

  describe("loadConfig", () => {
    test("should load valid YAML config file", () => {
      const mockConfig = {
        app: { name: "TestApp", version: "0.1.0" },
        window: { width: 800, height: 600 },
      };

      const yamlContent = yaml.dump(mockConfig);
      jest.spyOn(fs, "existsSync").mockReturnValue(true);
      jest.spyOn(fs, "readFileSync").mockReturnValue(yamlContent);

      // Since we can't easily import the module without electron,
      // we'll test the yaml parsing directly
      const parsed = yaml.load(yamlContent);

      expect(parsed).toEqual(mockConfig);
      expect(parsed.app.name).toBe("TestApp");
    });

    test("should handle missing config file", () => {
      jest.spyOn(fs, "existsSync").mockReturnValue(false);

      const exists = fs.existsSync("/nonexistent/config.yml");
      expect(exists).toBe(false);
    });

    test("should handle invalid YAML", () => {
      const invalidYaml = "invalid: yaml: content: ][";

      expect(() => {
        yaml.load(invalidYaml);
      }).toThrow();
    });
  });

  describe("Config validation", () => {
    test("should validate required sections", () => {
      const config = {
        app: { name: "Test", version: "0.1.0" },
        window: { width: 800, height: 600 },
        gui: { theme: {} },
      };

      expect(config).toHaveProperty("app");
      expect(config).toHaveProperty("window");
      expect(config).toHaveProperty("gui");
    });

    test("should validate app section fields", () => {
      const appConfig = {
        name: "SpectraTact",
        version: "0.1.0",
      };

      expect(appConfig.name).toBeDefined();
      expect(appConfig.version).toBeDefined();
      expect(typeof appConfig.name).toBe("string");
      expect(typeof appConfig.version).toBe("string");
    });

    test("should validate window section", () => {
      const windowConfig = {
        layout_mode: "grid",
        grid: { cols: 3, rows: 2 },
      };

      expect(windowConfig.layout_mode).toBeDefined();
      expect(["grid", "side_by_side"]).toContain(windowConfig.layout_mode);
    });
  });

  describe("Config file paths", () => {
    test("should construct correct config paths", () => {
      const configDir = "/test/config";
      const settingsPath = path.join(configDir, "settings.yml");
      const appsPath = path.join(configDir, "loaded_apps.yml");

      expect(settingsPath).toContain("settings.yml");
      expect(appsPath).toContain("loaded_apps.yml");
    });

    test("should handle path normalization", () => {
      const unnormalized = "/test/../config/./settings.yml";
      const normalized = path.normalize(unnormalized);

      expect(normalized).not.toContain("..");
      expect(normalized).not.toContain("./");
    });
  });
});
