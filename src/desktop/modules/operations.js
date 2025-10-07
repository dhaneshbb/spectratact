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
 * Application Operations Module
 */

export class OperationsManager {
  constructor(manager) {
    this.manager = manager;
  }

  async startApps() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Initializing applications...");

    const startTime = Date.now();
    try {
      const selectedAppsToLoad = this.manager.apps.filter((app) => app.selected);

      if (selectedAppsToLoad.length > 0) {
        this.manager.updateStatus(
          `Loading ${selectedAppsToLoad.length} selected apps (optimized)...`
        );

        const loadPromises = selectedAppsToLoad.map(async (app) => {
          try {
            const loadResult = await this.manager.electronAPI("loadSelectedProfiles", {
              appName: app.name,
              profiles: [
                {
                  profile: app.profile || "default",
                  app_path: app.app_path,
                },
              ],
            });
            if (loadResult && loadResult.success) {
              console.log(`Loaded ${app.name} to configuration`);
            } else {
              console.warn(`Failed to load ${app.name}:`, loadResult?.error || 'Unknown error');
            }
            return { app: app.name, success: true };
          } catch (loadError) {
            console.warn(`✗ Failed to load ${app.name}:`, loadError);
            return { app: app.name, success: false, error: loadError.message };
          }
        });

        const loadResults = await Promise.all(loadPromises);
        const successCount = loadResults.filter((r) => r.success).length;
        const failedCount = loadResults.length - successCount;

        if (successCount > 0) {
          await this.manager.reloadConfigurationAndUI();
          this.manager.updateStatus(
            `${successCount} apps loaded${
              failedCount > 0 ? ` (${failedCount} failed)` : ""
            }, starting...`
          );
        } else {
          this.manager.updateStatus(
            "No apps could be loaded, using existing configuration..."
          );
        }
      } else {
        this.manager.updateStatus("Starting with current configuration...");
      }

      const result = await this.manager.electronAPI("startApps");
      console.log("Start result:", result);

      const appCount = result.count || result.launched || 0;
      const totalApps = result.total || appCount;
      const failedApps = result.failed || [];
      const validApps = result.valid_apps || appCount;
      const invalidApps = result.invalid_apps || 0;
      const backendTime = result.elapsed_time || 0;
      const appsPerSecond = result.apps_per_second || 0;
      const success = result.success !== false && appCount > 0;

      console.log("Performance metrics:", {
        launched: appCount,
        total: totalApps,
        valid: validApps,
        invalid: invalidApps,
        backendTime: backendTime + "s",
        throughput: appsPerSecond + " apps/s",
      });

      if (success) {
        let statusMessage = `Started ${appCount} apps`;
        if (backendTime > 0) {
          statusMessage += ` in ${backendTime}s`;
          if (appsPerSecond > 0) {
            statusMessage += ` (${appsPerSecond} apps/s)`;
          }
        }
        if (totalApps > appCount) {
          statusMessage += ` • ${totalApps - appCount} failed`;
        }
        statusMessage += ", arranging...";
        this.manager.updateStatus(statusMessage);

        const arrangementDelay = Math.max(1000, Math.min(2000, appCount * 200));

        setTimeout(async () => {
          try {
            await this.manager.electronAPI("maximizeGrid");
            this.manager.refreshActiveApps();

            let finalMessage = `Started ${appCount} apps successfully`;
            if (backendTime > 0) {
              finalMessage += ` (${backendTime}s total)`;
            }
            if (failedApps.length > 0) {
              finalMessage += ` • ${failedApps.length} failed`;
              console.warn("Failed apps:", failedApps);
            }
            this.manager.updateStatus(finalMessage);

            if (this.manager.appConfig?.auto_unload_after_start) {
              setTimeout(() => {
                this.autoUnloadAfterStart();
              }, 3000);
            }
          } catch (error) {
            console.warn("Arrangement failed:", error);
            this.manager.updateStatus(`Started ${appCount} apps (arrangement failed)`);
          }
          this.manager.setLoading(false);
        }, arrangementDelay);
      } else {
        let errorMessage = "No applications started";
        if (result.error) {
          errorMessage += ` - ${result.error}`;
        } else if (failedApps.length > 0) {
          errorMessage += ` - check paths for: ${failedApps
            .slice(0, 3)
            .join(", ")}`;
          if (failedApps.length > 3) {
            errorMessage += ` and ${failedApps.length - 3} others`;
          }
        } else {
          errorMessage += " - check configuration";
        }
        this.manager.updateStatus(errorMessage);
        this.manager.setLoading(false);
      }
    } catch (error) {
      console.error("Error starting apps:", error);
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      this.manager.updateStatus(`Error starting applications after ${elapsed}s`);
    } finally {
      this.manager.setLoading(false);
    }
  }

  async autoUnloadAfterStart() {
    try {
      console.log("Auto-unload after start initiated...");
      this.manager.updateStatus("Auto-unloading apps after successful start...");

      await this.manager.refreshActiveApps();
      const activeAppCount = this.manager.activeApps.length;

      const result = await this.manager.electronAPI("unloadAllProfiles");

      if (result && result.success) {
        await this.manager.reloadConfigurationAndUI();

        this.manager.updateStatus(
          `${activeAppCount} apps running, configs auto-unloaded for clean start next time`
        );

        setTimeout(() => {
          this.manager.updateStatus(
            `${activeAppCount} apps active - configurations cleared`
          );
        }, 2000);
      } else {
        console.warn("Auto-unload failed:", result?.error);
        this.manager.updateStatus("Auto-unload failed - apps still running");
      }
    } catch (error) {
      console.error("Error during auto-unload:", error);
      this.manager.updateStatus("Auto-unload error - apps still running");
    }
  }

  async arrangeGrid() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Arranging windows in grid...");

    // OPTIMISTIC UPDATE: Instantly show as active/restored (if enabled)
    const optimisticEnabled = this.manager.appConfig?.performance?.ui_updates?.optimistic_updates !== false;

    if (optimisticEnabled && this.manager.activeApps && this.manager.activeApps.length > 0) {
      this.manager.activeApps = this.manager.activeApps.map(app => ({
        ...app,
        is_minimized: false
      }));
      this.manager.appsManager.renderAppGridOptimized();

      const statusText = document.getElementById("status-text");
      if (statusText) {
        statusText.textContent = `${this.manager.activeApps.length} apps running`;
      }
    }

    try {
      const result = await this.manager.electronAPI("maximizeGrid");
      if (result.success !== false) {
        // INSTANT UPDATE: Use embedded active_apps from backend response
        if (result.active_apps && Array.isArray(result.active_apps)) {
          this.manager.activeApps = result.active_apps;
          this.manager.appsManager.renderAppGridOptimized();

          const statusText = document.getElementById("status-text");
          if (statusText) {
            statusText.textContent = `${result.active_apps.length} apps running`;
          }
        }

        this.manager.updateStatus(`Arranged ${result.count || 0} windows in grid`);
      } else {
        this.manager.updateStatus("Failed to arrange windows: " + result.error);
        // Revert optimistic update on failure
        this.manager.refreshActiveApps();
      }
    } catch (error) {
      console.error("Error arranging grid:", error);
      this.manager.updateStatus("Error arranging windows");
      this.manager.refreshActiveApps();
    } finally {
      this.manager.setLoading(false);
    }
  }

  async toggleLayoutMode() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Switching layout mode...");

    try {
      const currentMode = this.manager.appConfig?.window?.layout_mode || "grid";
      const newMode = currentMode === "grid" ? "side_by_side" : "grid";

      console.log(`Switching from ${currentMode} to ${newMode} layout`);

      const configResult = await this.manager.electronAPI("updateLayoutMode", {
        layout_mode: newMode,
      });

      if (!configResult.success) {
        this.manager.updateStatus(
          "Failed to update layout configuration: " +
            (configResult.error || "Unknown error")
        );
        return;
      }

      if (this.manager.appConfig && this.manager.appConfig.window) {
        this.manager.appConfig.window.layout_mode = newMode;
      }

      this.manager.updateLayoutModeUI(newMode);

      this.manager.updateStatus(
        `Switching to ${newMode === "grid" ? "Grid" : "Side-by-Side"} layout...`
      );

      const arrangeResult = await this.manager.electronAPI("maximizeGrid");

      if (arrangeResult.success !== false) {
        const windowCount = arrangeResult.count || 0;
        this.manager.updateStatus(
          `Switched to ${
            newMode === "grid" ? "Grid" : "Side-by-Side"
          } layout (${windowCount} windows arranged)`
        );

        setTimeout(() => {
          this.manager.refreshActiveApps();
        }, 500);
      } else {
        this.manager.updateStatus(
          `Layout mode updated to ${
            newMode === "grid" ? "Grid" : "Side-by-Side"
          } but arrangement failed: ${arrangeResult.error || "Unknown error"}`
        );
      }
    } catch (error) {
      console.error("Error toggling layout mode:", error);
      this.manager.updateStatus("Error switching layout mode: " + error.message);
    } finally {
      this.manager.setLoading(false);
    }
  }

  async minimizeAll() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Minimizing all windows...");

    // OPTIMISTIC UPDATE: Instantly update UI before backend responds (if enabled)
    const optimisticEnabled = this.manager.appConfig?.performance?.ui_updates?.optimistic_updates !== false;

    if (optimisticEnabled && this.manager.activeApps && this.manager.activeApps.length > 0) {
      this.manager.activeApps = this.manager.activeApps.map(app => ({
        ...app,
        is_minimized: true
      }));
      this.manager.appsManager.renderAppGridOptimized();

      const statusIndicator = document.getElementById("status-indicator");
      const statusText = document.getElementById("status-text");
      if (statusText) {
        statusText.textContent = `${this.manager.activeApps.length} apps running (minimized)`;
      }
    }

    try {
      const result = await this.manager.electronAPI("minimizeAll");
      if (result.success !== false) {
        // INSTANT UPDATE: Use embedded active_apps from backend response
        if (result.active_apps && Array.isArray(result.active_apps)) {
          this.manager.activeApps = result.active_apps;
          this.manager.appsManager.renderAppGridOptimized();

          const statusText = document.getElementById("status-text");
          if (statusText) {
            statusText.textContent = `${result.active_apps.length} apps running`;
          }
        }

        this.manager.updateStatus(`Minimized ${result.count || 0} windows`);
      } else {
        this.manager.updateStatus("Failed to minimize windows: " + result.error);
        // Revert optimistic update on failure
        this.manager.refreshActiveApps();
      }
    } catch (error) {
      console.error("Error minimizing windows:", error);
      this.manager.updateStatus("Error minimizing windows");
      // Revert optimistic update on error
      this.manager.refreshActiveApps();
    } finally {
      this.manager.setLoading(false);
    }
  }

  async closeAllApps() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Closing all applications...");

    try {
      const result = await this.manager.electronAPI("closeAll");
      if (result.success !== false) {
        this.manager.updateStatus(`Closed ${result.count || 0} applications`);
        await this.manager.refreshActiveApps();
      } else {
        this.manager.updateStatus("Failed to close applications: " + result.error);
      }
    } catch (error) {
      console.error("Error closing apps:", error);
      this.manager.updateStatus("Error closing applications");
    } finally {
      this.manager.setLoading(false);
    }
  }

  async reopenAllApps() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Restarting all applications...");

    try {
      await this.manager.electronAPI("closeAll");
      setTimeout(async () => {
        const result = await this.manager.electronAPI("startApps");
        if (result.success !== false) {
          this.manager.updateStatus(`Restarted ${result.count || 0} applications`);
          await this.manager.refreshActiveApps();
        } else {
          this.manager.updateStatus("Failed to restart applications: " + result.error);
        }
        this.manager.setLoading(false);
      }, 2000);
    } catch (error) {
      console.error("Error restarting apps:", error);
      this.manager.updateStatus("Error restarting applications");
      this.manager.setLoading(false);
    }
  }

  async refreshAllApps() {
    if (this.manager.isLoading) return;

    this.manager.setLoading(true);
    this.manager.updateStatus("Reliable refresh to ALL apps...");

    const startTime = performance.now();

    try {
      const result = await this.manager.electronAPI("refreshAllPages");

      const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);

      if (result.success !== undefined) {
        if (result.failed > 0) {
          this.manager.updateStatus(
            `Refreshed ${result.success}/${result.total} apps in ${elapsed}s (${result.failed} failed)`
          );
        } else {
          this.manager.updateStatus(
            `SUCCESS: ALL ${result.success} apps refreshed in ${elapsed}s (perfect!)`
          );
        }

        setTimeout(() => this.manager.refreshActiveApps(), 300);
      } else {
        this.manager.updateStatus("Reliable refresh completed");
      }
    } catch (error) {
      console.error('Refresh failed:', error);
      this.manager.updateStatus(`Refresh error: ${error.message}`);
    } finally {
      this.manager.setLoading(false);
    }
  }
}
