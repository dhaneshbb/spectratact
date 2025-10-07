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
 * Load Apps Panel Module
 */

export class LoadAppsManager {
  constructor(manager) {
    this.manager = manager;
  }

  async loadAllAvailableApps() {
    try {
      console.log("Loading available apps from backend...");
      const loadAppsConfig = await this.manager.electronAPI("getLoadAppsConfig");
      console.log("Received loadAppsConfig:", loadAppsConfig);

      if (!loadAppsConfig) {
        console.error("No response from backend");
        this.renderEmptyAppsTable("No response from backend");
        return;
      }

      if (loadAppsConfig.success === false) {
        console.error("Backend error:", loadAppsConfig.error);
        this.renderEmptyAppsTable(`Backend error: ${loadAppsConfig.error}`);
        return;
      }

      if (loadAppsConfig.apps && Object.keys(loadAppsConfig.apps).length > 0) {
        console.log(
          `Found ${Object.keys(loadAppsConfig.apps).length} app types:`,
          Object.keys(loadAppsConfig.apps)
        );
        console.log("Full apps data:", loadAppsConfig.apps);
        this.renderAppsTable(loadAppsConfig.apps);
        this.manager.updateStatus("Load Apps data loaded successfully");
      } else {
        console.warn("apps is empty or missing");
        console.warn("Available keys:", Object.keys(loadAppsConfig || {}));
        console.warn("Full loadAppsConfig:", loadAppsConfig);
        this.renderEmptyAppsTable("No applications found in configuration");
      }
    } catch (error) {
      console.error("Exception loading available apps:", error);
      console.error("Error stack:", error.stack);
      this.renderEmptyAppsTable(`Error: ${error.message}`);
    }
  }

  renderAppsTable(desktopApplications) {
    const tableBody = document.getElementById("apps-table-body");
    tableBody.innerHTML = "";

    this.manager.availableApps = desktopApplications;

    this.populateProfileDropdown(desktopApplications);

    Object.keys(desktopApplications).forEach((appName) => {
      const platformData = desktopApplications[appName];
      const apps = platformData.profiles || [];
      const row = document.createElement("tr");

      row.innerHTML = `
        <td class="app-name-cell">${appName.replace(/_/g, " ")}</td>
        <td class="user-profiles-cell">
          <div class="profile-chips">
            ${apps
              .map(
                (app) => `
              <div class="profile-chip ${
                app.enabled ? "enabled" : ""
              }"
                   data-app-name="${appName}"
                   data-profile="${app.profile}"
                   data-app-path="${app.app_path}">
                ${app.profile}
              </div>
            `
              )
              .join("")}
          </div>
        </td>
      `;

      tableBody.appendChild(row);
    });

    this.setupAppsTableEventListeners();
  }

  populateProfileDropdown(desktopApplications) {
    const dropdown = document.getElementById("profile-filter-select");
    const profiles = new Set();

    Object.values(desktopApplications).forEach((platformData) => {
      const apps = platformData.profiles || [];
      apps.forEach((app) => {
        profiles.add(app.profile);
      });
    });

    dropdown.innerHTML = '<option value="">-- Select by Profile --</option>';

    Array.from(profiles)
      .sort()
      .forEach((profile) => {
        const option = document.createElement("option");
        option.value = profile;
        option.textContent = profile;
        dropdown.appendChild(option);
      });
  }

  renderEmptyAppsTable(message = "No applications found in load_apps.yml") {
    const tableBody = document.getElementById("apps-table-body");
    tableBody.innerHTML = `
      <tr>
        <td colspan="2" style="text-align: center; color: var(--text-tertiary); padding: var(--spacing-xl);">
          <div>${message}</div>
          <div style="font-size: 11px; margin-top: 8px;">
            Check the browser console (F12) for more details
          </div>
        </td>
      </tr>
    `;
  }

  setupAppsTableEventListeners() {
    document.querySelectorAll(".profile-chip").forEach((chip) => {
      chip.addEventListener("click", async (e) => {
        e.preventDefault();

        if (chip.classList.contains("enabled")) {
          const profileName = chip.getAttribute("data-profile");
          const appName = chip.getAttribute("data-app-name");

          this.manager.unloadProfile(appName.replace(/_/g, " "), profileName);
        } else {
          const profileName = chip.getAttribute("data-profile");
          const appName = chip.getAttribute("data-app-name");
          const appPath = chip.getAttribute("data-app-path");

          await this.manager.loadSingleProfile(
            appName.replace(/_/g, " "),
            profileName,
            appPath
          );
        }
      });
    });
  }

  async loadAllAppsForSelectedProfile() {
    try {
      const selectedProfile = document.getElementById(
        "profile-filter-select"
      ).value;

      if (!selectedProfile) {
        this.manager.updateStatus("No profile selected");
        return;
      }

      if (!this.manager.availableApps) {
        this.manager.updateStatus("No available apps data found");
        return;
      }

      this.manager.setLoading(true);
      this.manager.updateStatus(`Loading all apps for profile: ${selectedProfile}...`);

      await this.manager.unloadAllApps();

      const appsToLoad = [];

      Object.keys(this.manager.availableApps).forEach((appName) => {
        const platformData = this.manager.availableApps[appName];
        const apps = platformData.profiles || [];
        const profileApp = apps.find((app) => app.profile === selectedProfile);

        if (profileApp) {
          appsToLoad.push({
            appName: appName.replace(/_/g, " "),
            profile: profileApp.profile,
            app_path: profileApp.app_path,
          });
        }
      });

      if (appsToLoad.length === 0) {
        this.manager.updateStatus(`No apps found for profile: ${selectedProfile}`);
        return;
      }

      console.log(
        `Loading ${appsToLoad.length} apps for profile ${selectedProfile}:`,
        appsToLoad
      );

      let successCount = 0;
      let failCount = 0;

      for (const appData of appsToLoad) {
        try {
          const result = await this.manager.electronAPI("loadSelectedProfiles", {
            appName: appData.appName,
            profiles: [
              {
                profile: appData.profile,
                app_path: appData.app_path,
              },
            ],
          });

          if (result && result.success) {
            successCount++;
            console.log(`Loaded ${appData.appName} for ${selectedProfile}`);
          } else {
            failCount++;
            console.error(
              `✗ Failed to load ${appData.appName}:`,
              result?.error
            );
          }
        } catch (error) {
          failCount++;
          console.error(`✗ Error loading ${appData.appName}:`, error);
        }
      }

      await this.manager.reloadConfigurationAndUI();

      const totalApps = appsToLoad.length;
      if (successCount === totalApps) {
        this.manager.updateStatus(
          `Successfully loaded all ${totalApps} apps for profile: ${selectedProfile}`
        );
      } else {
        this.manager.updateStatus(
          `Loaded ${successCount}/${totalApps} apps for profile: ${selectedProfile} (${failCount} failed)`
        );
      }

      document.getElementById("profile-filter-select").value = "";
      document.getElementById("load-all-for-profile-btn").disabled = true;
    } catch (error) {
      console.error("Error loading all apps for profile:", error);
      this.manager.updateStatus(`Error loading apps for profile: ${error.message}`);
    } finally {
      this.manager.setLoading(false);
    }
  }
}
