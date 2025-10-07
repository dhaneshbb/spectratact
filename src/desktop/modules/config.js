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

/**
 * Configuration Management Module
 */

export class ConfigManager {
  constructor(manager) {
    this.manager = manager;
  }

  async loadConfiguration() {
    try {
      console.log("Loading configuration from backend...");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      this.manager.appConfig = await this.manager.electronAPI("getConfig");
      console.log("Received config:", this.manager.appConfig);

      if (this.manager.appConfig && this.manager.appConfig.apps) {
        this.manager.apps = this.manager.appConfig.apps
          .filter((app) => app.enabled !== false)
          .map((app) => ({
            id: app.name.toLowerCase().replace(/\s+/g, "_"),
            name: app.name,
            enabled: app.enabled === true,
            selected: app.selected === true,
            priority: app.priority !== undefined ? app.priority : 999,
            app_path: app.app_path,
            keywords: app.keywords || [],
            profile: app.profile || "default",
          }));

        this.manager.apps.sort((a, b) => a.priority - b.priority);

        console.log("Loaded", this.manager.apps.length, "applications from config");
        console.log(
          "Priority-based order:",
          this.manager.apps
            .map((app) => `${app.name} (priority: ${app.priority})`)
            .join(", ")
        );
      } else {
        console.warn("No apps found in config, using empty array");
        this.manager.apps = [];
      }
    } catch (error) {
      console.error("Error loading configuration:", error);
      this.manager.apps = [];
    }
  }

  applyGridLayout() {
    if (this.manager.appConfig && this.manager.appConfig.window && this.manager.appConfig.window.grid) {
      const grid = this.manager.appConfig.window.grid;
      const cols = grid.cols || 3;
      const rows = grid.rows || 2;

      const appGrid = document.getElementById("app-grid");
      if (appGrid) {
        appGrid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
        appGrid.style.gridTemplateRows = `repeat(${rows}, auto)`;

        console.log(`Applied grid layout: ${cols}x${rows} from config`);
      }
    }
  }

  async reloadConfiguration() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Reloading configuration...");

    try {
      const result = await this.manager.electronAPI("reloadConfig");

      if (result.success) {
        await this.loadConfiguration();

        this.applyGridLayout();
        this.manager.renderAppGrid();
        this.manager.updateSelectedApps();
        this.manager.updateAppTitle();

        const currentMode = this.manager.appConfig?.window?.layout_mode || "grid";
        this.manager.updateLayoutModeUI(currentMode);

        this.manager.updateStatus(
          `Configuration reloaded - ${this.manager.apps.length} apps loaded`
        );
      } else {
        this.manager.updateStatus(
          "Failed to reload configuration: " + (result.error || "Unknown error")
        );
      }
    } catch (error) {
      console.error("Error reloading configuration:", error);
      this.manager.updateStatus("Error reloading configuration");
    } finally {
      this.manager.setLoading(false);
    }
  }

  async reloadConfigurationAndUI() {
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      const newConfig = await this.manager.electronAPI("getConfig");

      if (newConfig) {
        this.manager.appConfig = newConfig;

        if (newConfig && newConfig.apps) {
          this.manager.apps = newConfig.apps
            .filter((app) => app.enabled !== false)
            .map((app) => ({
              id: app.name.toLowerCase().replace(/\s+/g, "_"),
              name: app.name,
              enabled: app.enabled === true,
              selected: app.selected === true,
              priority: app.priority !== undefined ? app.priority : 999,
              app_path: app.app_path,
              keywords: app.keywords || [],
              profile: app.profile || "default",
            }));

          this.manager.apps.sort((a, b) => a.priority - b.priority);
          console.log("Reloaded", this.manager.apps.length, "applications from config");
        } else {
          console.warn("No apps found in reloaded config");
          this.manager.apps = [];
        }

        this.manager.renderAppGrid();
        this.manager.updateSelectedApps();

        await this.manager.refreshActiveApps();

        await this.manager.loadAllAvailableApps();

        setTimeout(() => {
          this.manager.updateStatus("Configuration reloaded successfully");
        }, 500);
      } else {
        console.warn("No configuration received from backend");
      }
    } catch (error) {
      console.error("Error reloading configuration:", error);
      this.manager.updateStatus("Error reloading configuration");
    }
  }

  updateAppTitle() {
    if (this.manager.appConfig && this.manager.appConfig.app && this.manager.appConfig.app.name) {
      const titleElement = document.querySelector(".app-title");
      if (titleElement) {
        titleElement.textContent = this.manager.appConfig.app.name;
        console.log("Updated app title from config:", this.manager.appConfig.app.name);
      }

      document.title = this.manager.appConfig.app.name;
    }
  }
}
