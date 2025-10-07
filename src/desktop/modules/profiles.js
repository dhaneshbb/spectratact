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
 * Profile Management Module
 */

export class ProfilesManager {
  constructor(manager) {
    this.manager = manager;
  }

  async loadSingleProfile(appName, profileName, appPath) {
    try {
      console.log(`Loading single profile: ${profileName} for ${appName}`);

      await this.manager.refreshActiveApps();
      const hasActiveSession = this.manager.activeApps && this.manager.activeApps.length > 0;

      if (hasActiveSession) {
        this.manager.updateStatus(`Switching ${appName} to ${profileName} profile...`);
        console.log(`ACTIVE SESSION MODE: Full switching for ${appName}`);

        const runningApp = this.manager.activeApps.find((app) => app.name === appName);
        if (runningApp) {
          console.log(`Found running app ${appName}, closing it first...`);
          this.manager.updateStatus(`Closing existing ${appName} app...`);

          try {
            await this.manager.electronAPI("closeSpecificApp", { name: appName });
            console.log(`Closed ${appName} app successfully`);
            await new Promise((resolve) => setTimeout(resolve, 1000));
          } catch (closeError) {
            console.warn(`Failed to close ${appName}:`, closeError);
          }
        }
      } else {
        this.manager.updateStatus(
          `Loading ${profileName} profile for ${appName} (config only)...`
        );
        console.log(
          `CONFIG-ONLY MODE: Only updating configuration for ${appName}`
        );
      }

      this.manager.updateStatus(`Loading ${profileName} profile for ${appName}...`);
      const result = await this.manager.electronAPI("loadSelectedProfiles", {
        appName: appName,
        profiles: [
          {
            profile: profileName,
            app_path: appPath,
          },
        ],
      });

      if (result && result.success) {
        console.log("Profile loaded successfully:", result);

        await this.manager.reloadConfigurationAndUI();

        this.manager.updateStatus(
          `Verifying ${profileName} profile is loaded for ${appName}...`
        );

        try {
          await this.manager.electronAPI("reloadConfig");
          console.log(`BACKEND CONFIG RELOADED for ${appName} profile switch`);
        } catch (reloadError) {
          console.warn(`Backend reload failed:`, reloadError);
        }

        await new Promise((resolve) => setTimeout(resolve, 1000));

        const verifyConfig = await this.manager.electronAPI("getConfig");
        if (verifyConfig && verifyConfig.apps) {
          const matchingApp = verifyConfig.apps.find(
            (app) => app.name === appName && app.profile === profileName
          );
          if (matchingApp) {
            console.log(
              `VERIFIED: ${appName} profile '${profileName}' loaded with path: ${matchingApp.app_path}`
            );
          } else {
            console.warn(
              `VERIFICATION FAILED: ${appName} profile '${profileName}' not found in backend config`
            );
            this.manager.updateStatus(
              `Profile loading verification failed for ${appName}`
            );
            return;
          }
        }

        if (hasActiveSession) {
          this.manager.updateStatus(
            `Opening ${appName} with ${profileName} profile...`
          );

          try {
            const launchResult = await this.manager.electronAPI("openSpecificApp", {
              name: appName,
            });
            console.log(
              `Launch result for ${appName} with ${profileName}:`,
              launchResult
            );

            if (
              launchResult &&
              launchResult.success &&
              launchResult.count > 0
            ) {
              this.manager.updateStatus(
                `${appName} launched with ${profileName}, arranging windows...`
              );

              setTimeout(async () => {
                try {
                  const arrangeResult = await this.manager.electronAPI("maximizeGrid");
                  console.log(
                    `Window arrangement result after profile switch:`,
                    arrangeResult
                  );

                  if (arrangeResult && arrangeResult.success !== false) {
                    const windowCount = arrangeResult.count || 0;
                    this.manager.updateStatus(
                      `${appName} switched to ${profileName} - ${windowCount} windows arranged`
                    );
                  } else {
                    this.manager.updateStatus(
                      `${appName} switched to ${profileName} (arrangement failed)`
                    );
                  }

                  await this.manager.refreshActiveApps();
                } catch (arrangeError) {
                  console.warn(
                    `Window arrangement failed after profile switch:`,
                    arrangeError
                  );
                  this.manager.updateStatus(
                    `${appName} switched to ${profileName} (windows not arranged)`
                  );
                }
              }, 2000);
            } else {
              this.manager.updateStatus(
                `Profile switched to ${profileName} for ${appName} (launch failed - check logs)`
              );
            }
          } catch (launchError) {
            console.warn(
              `Failed to launch ${appName} with new profile:`,
              launchError
            );
            this.manager.updateStatus(
              `Profile switched but launch failed for ${appName}`
            );
          }
        } else {
          this.manager.updateStatus(
            `Profile ${profileName} loaded for ${appName} (use "Start Apps" to launch)`
          );
          console.log(
            `CONFIG-ONLY: Profile ${profileName} loaded for ${appName} without launching app`
          );
        }
      } else {
        this.manager.updateStatus(
          `Failed to load profile: ${result?.error || "Unknown error"}`
        );
      }
    } catch (error) {
      console.error("Error loading single profile:", error);
      this.manager.updateStatus(`Error loading profile: ${error.message}`);
    }
  }

  async unloadProfile(appName, profileName) {
    try {
      console.log(`UNLOAD PROFILE: ${profileName} for ${appName}`);

      await this.manager.refreshActiveApps();
      const hasActiveSession = this.manager.activeApps && this.manager.activeApps.length > 0;

      if (hasActiveSession) {
        this.manager.updateStatus(
          `Closing ${appName} and unloading ${profileName} profile...`
        );
        console.log(
          `ACTIVE SESSION MODE: Full unload with app closing for ${appName}`
        );

        const normalizeAppName = (name) => {
          return name
            .toLowerCase()
            .replace(/\s+/g, " ")
            .replace(/_/g, " ")
            .replace(" mode", "")
            .trim();
        };

        const targetNormalized = normalizeAppName(appName);
        const runningApp = this.manager.activeApps.find((app) => {
          const appNormalized = normalizeAppName(app.name);
          return (
            appNormalized === targetNormalized ||
            app.name.toLowerCase() === appName.toLowerCase() ||
            app.name.includes(appName) ||
            appName.includes(app.name)
          );
        });

        if (runningApp) {
          console.log(
            `FOUND RUNNING APP: '${runningApp.name}' (target: '${appName}')`
          );
          this.manager.updateStatus(`Closing ${runningApp.name} app...`);

          try {
            const closeResult = await this.manager.electronAPI("closeSpecificApp", {
              name: runningApp.name,
            });
            console.log(`Close result for ${runningApp.name}:`, closeResult);

            let appClosed = false;
            for (let i = 0; i < 5; i++) {
              await new Promise((resolve) => setTimeout(resolve, 800));
              await this.manager.refreshActiveApps();
              const stillRunning = this.manager.activeApps.find(
                (app) =>
                  normalizeAppName(app.name) ===
                  normalizeAppName(runningApp.name)
              );
              if (!stillRunning) {
                appClosed = true;
                console.log(
                  `VERIFIED: ${runningApp.name} is closed after ${
                    (i + 1) * 800
                  }ms`
                );
                break;
              }
              console.log(
                `Still waiting for ${runningApp.name} to close... (attempt ${
                  i + 1
                })`
              );
            }

            if (!appClosed) {
              console.warn(`WARNING: ${runningApp.name} may still be running`);
            }
          } catch (closeError) {
            console.warn(`Failed to close ${runningApp.name}:`, closeError);
          }
        } else {
          console.log(`No running app found for ${appName}`);
        }
      } else {
        this.manager.updateStatus(
          `Unloading ${profileName} profile for ${appName} (config only)...`
        );
        console.log(
          `CONFIG-ONLY MODE: Only removing profile from configuration for ${appName}`
        );
      }

      this.manager.updateStatus(`Removing ${profileName} from configuration...`);
      const result = await this.manager.electronAPI("unloadProfile", {
        appName: appName,
        profileName: profileName,
        closeWindows: true  // Always close windows on unload
      });

      if (result && result.success) {
        console.log(`PROFILE UNLOADED: ${profileName} from ${appName}`, result);

        // If backend indicates windows should be closed, close them explicitly
        if (result.should_close_windows && result.app_name) {
          console.log(`Closing windows for ${result.app_name} as requested by backend`);
          try {
            await this.manager.electronAPI("closeSpecificApp", { name: result.app_name });
            await new Promise((resolve) => setTimeout(resolve, 800));
          } catch (closeError) {
            console.warn(`Failed to close windows for ${result.app_name}:`, closeError);
          }
        }

        await this.manager.reloadConfigurationAndUI();

        await new Promise((resolve) => setTimeout(resolve, 500));
        await this.manager.refreshActiveApps();

        if (hasActiveSession) {
          if (this.manager.activeApps && this.manager.activeApps.length > 0) {
            this.manager.updateStatus(
              `Arranging remaining ${this.manager.activeApps.length} windows...`
            );

            setTimeout(async () => {
              try {
                await this.manager.electronAPI("maximizeGrid");
                this.manager.updateStatus(
                  `${profileName} unloaded, ${this.manager.activeApps.length} windows arranged`
                );
              } catch (arrangeError) {
                console.warn(
                  "Failed to arrange windows after unloading:",
                  arrangeError
                );
                this.manager.updateStatus(`${profileName} unloaded from ${appName}`);
              }
            }, 1500);
          } else {
            this.manager.updateStatus(
              `${profileName} unloaded from ${appName} - no apps running`
            );
          }
        } else {
          this.manager.updateStatus(
            `Profile ${profileName} unloaded from ${appName} (config only)`
          );
          console.log(
            `CONFIG-ONLY: Profile ${profileName} removed from configuration for ${appName}`
          );
        }
      } else {
        this.manager.updateStatus(`Failed to unload profile: ${result?.error}`);
      }
    } catch (error) {
      console.error("Error unloading profile:", error);
      this.manager.updateStatus(`Error unloading profile: ${error.message}`);
    }
  }

  async unloadAllApps() {
    if (this.manager.isLoading) {
      console.log("Unload already in progress, ignoring request");
      return;
    }

    try {
      this.manager.setLoading(true);
      console.log("Starting unload all process...");
      this.manager.updateStatus("Unloading all applications...");

      console.log("Attempting to close all running applications...");
      try {
        this.manager.electronAPI("closeAll");
        this.manager.updateStatus("Fast closing & unloading all...");
        await new Promise((resolve) => setTimeout(resolve, 500));
      } catch (closeError) {
        console.warn("Fast close failed:", closeError);
      }

      console.log("Clearing loaded_apps.yml...");
      this.manager.updateStatus("Clearing all profiles from configuration...");

      const result = await this.manager.electronAPI("unloadAllProfiles");

      if (result && result.success) {
        console.log("All profiles unloaded successfully:", result);

        this.manager.apps = [];
        this.manager.activeApps = [];
        this.manager.selectedApps.clear();

        this.manager.renderAppGrid();
        this.manager.updateSelectedApps();

        try {
          await this.manager.reloadConfigurationAndUI();
        } catch (reloadError) {
          console.warn(
            "Warning: Could not reload config after unload:",
            reloadError
          );
        }

        this.manager.updateStatus(
          `Fast unloaded all ${result.count || 0} applications`
        );

        setTimeout(() => {
          this.manager.updateStatus("Ready for new profiles");
        }, 1000);
      } else {
        console.error("Unload failed:", result);
        this.manager.updateStatus(
          `Failed to unload applications: ${result?.error || "Unknown error"}`
        );
      }
    } catch (error) {
      console.error("Error unloading all applications:", error);
      this.manager.updateStatus(`Error unloading applications: ${error.message}`);
    } finally {
      this.manager.setLoading(false);
      console.log("Unload all process completed");
    }
  }

  async unloadSelectedApps() {
    if (this.manager.isLoading) {
      console.log("Unload already in progress, ignoring request");
      return;
    }

    if (this.manager.selectedApps.size === 0) {
      this.manager.updateStatus("No apps selected to unload");
      return;
    }

    try {
      this.manager.setLoading(true);
      const selectedAppNames = Array.from(this.manager.selectedApps);
      console.log(`Unloading ${selectedAppNames.length} selected apps:`, selectedAppNames);
      this.manager.updateStatus(`Unloading ${selectedAppNames.length} selected app(s)...`);

      let successCount = 0;
      let failCount = 0;

      for (const appName of selectedAppNames) {
        try {
          const app = this.manager.apps.find(a => a.name === appName);
          if (!app) {
            console.warn(`App ${appName} not found in apps list`);
            failCount++;
            continue;
          }

          // First close the running windows
          try {
            await this.manager.electronAPI("closeSpecificApp", { name: appName });
            console.log(`Closed windows for ${appName}`);
            await new Promise((resolve) => setTimeout(resolve, 500));
          } catch (closeError) {
            console.warn(`Failed to close windows for ${appName}:`, closeError);
          }

          // Then unload the profile from config
          const result = await this.manager.electronAPI("unloadProfile", {
            appName: appName,
            profileName: app.profile || "default",
            closeWindows: false  // Already closed above
          });

          if (result && result.success) {
            console.log(`Successfully unloaded ${appName}`);
            successCount++;
          } else {
            console.error(`Failed to unload ${appName}:`, result?.error);
            failCount++;
          }
        } catch (error) {
          console.error(`Error unloading ${appName}:`, error);
          failCount++;
        }
      }

      await this.manager.reloadConfigurationAndUI();

      if (successCount > 0 && failCount === 0) {
        this.manager.updateStatus(`Successfully unloaded ${successCount} app(s)`);
      } else if (successCount > 0 && failCount > 0) {
        this.manager.updateStatus(`Unloaded ${successCount} app(s), ${failCount} failed`);
      } else {
        this.manager.updateStatus(`Failed to unload selected apps`);
      }

      setTimeout(() => {
        this.manager.clearSelection();
      }, 1000);

    } catch (error) {
      console.error("Error unloading selected applications:", error);
      this.manager.updateStatus(`Error unloading selected apps: ${error.message}`);
    } finally {
      this.manager.setLoading(false);
      console.log("Unload selected process completed");
    }
  }
}
