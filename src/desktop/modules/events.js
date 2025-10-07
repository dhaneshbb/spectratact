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
 * Event Listeners Module
 */

export class EventsManager {
  constructor(manager) {
    this.manager = manager;
  }

  setupEventListeners() {
    document.getElementById("minimize-btn").addEventListener("click", () => {
      this.manager.electronAPI("windowMinimize");
    });

    document.getElementById("maximize-btn").addEventListener("click", () => {
      this.manager.electronAPI("windowMaximize");
    });

    document.getElementById("close-btn").addEventListener("click", () => {
      this.manager.electronAPI("windowClose");
    });

    document.getElementById("start-apps-btn").addEventListener("click", () => {
      this.manager.startApps();
    });

    document.getElementById("close-all-btn").addEventListener("click", () => {
      this.manager.closeAllApps();
    });

    document.getElementById("reopen-all-btn").addEventListener("click", () => {
      this.manager.reopenAllApps();
    });

    document
      .getElementById("arrange-grid-btn")
      .addEventListener("click", () => {
        this.manager.arrangeGrid();
      });

    document.getElementById("layout-mode-btn").addEventListener("click", () => {
      this.manager.toggleLayoutMode();
    });

    document
      .getElementById("minimize-all-btn")
      .addEventListener("click", () => {
        this.manager.minimizeAll();
      });

    document
      .getElementById("refresh-apps-btn")
      .addEventListener("click", () => {
        this.manager.refreshAllApps();
      });

    document.getElementById("unload-all-btn").addEventListener("click", () => {
      this.manager.unloadAllApps();
    });

    document
      .getElementById("theme-toggle-btn")
      .addEventListener("click", () => {
        this.manager.toggleTheme();
      });

    document.getElementById("help-btn").addEventListener("click", () => {
      this.manager.showHelpModal();
    });

    document.getElementById("help-close-btn").addEventListener("click", () => {
      this.manager.hideHelpModal();
    });
    document.getElementById("help-modal").addEventListener("click", (e) => {
      if (e.target.id === "help-modal") {
        this.manager.hideHelpModal();
      }
    });

    document.getElementById("select-all-btn").addEventListener("click", () => {
      this.manager.selectAllApps();
    });

    document
      .getElementById("clear-selection-btn")
      .addEventListener("click", () => {
        this.manager.clearSelection();
      });

    document
      .getElementById("panel-toggle-btn")
      .addEventListener("click", () => {
        this.manager.toggleLeftPanel();
      });

    document
      .getElementById("collapsed-expand-btn")
      .addEventListener("click", () => {
        this.manager.expandLeftPanel();
      });

    const menuButton = document.getElementById("menu-btn-dropdown");
    if (menuButton) {
      menuButton.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log("Menu button clicked!");
        this.manager.toggleMenuMenu();
      });
      console.log("Menu button click listener attached");
    } else {
      console.error("Menu button not found!");
    }

    document.getElementById("dropdown-close").addEventListener("click", () => {
      this.manager.hideMenuMenu();
    });

    this.setupMenuMenuHandlers();

    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey) {
        switch (e.key) {
          case "s":
            e.preventDefault();
            this.manager.startApps();
            break;
          case "a":
            e.preventDefault();
            this.manager.selectAllApps();
            break;
          case "d":
            e.preventDefault();
            this.manager.clearSelection();
            break;
          case "g":
            e.preventDefault();
            this.manager.arrangeGrid();
            break;
        }
      }
    });

    document.addEventListener("click", (e) => {
      if (
        !e.target.closest(".dropdown-menu") &&
        !e.target.closest("#menu-btn-dropdown")
      ) {
        this.manager.hideMenuMenu();
      }
    });

    document.getElementById("help-close-btn").addEventListener("click", () => {
      this.manager.hideHelpModal();
    });

    document.getElementById("help-modal").addEventListener("click", (e) => {
      if (e.target.id === "help-modal") {
        this.manager.hideHelpModal();
      }
    });

    document
      .getElementById("profile-filter-select")
      .addEventListener("change", (e) => {
        const selectedProfile = e.target.value;
        const loadButton = document.getElementById("load-all-for-profile-btn");
        loadButton.disabled = !selectedProfile;
      });

    document
      .getElementById("load-all-for-profile-btn")
      .addEventListener("click", () => {
        this.manager.loadAllAppsForSelectedProfile();
      });

    document
      .getElementById("unload-selected-btn")
      .addEventListener("click", () => {
        this.manager.unloadSelectedApps();
      });

    this.manager.setupDragAndDrop();
  }

  setupMenuMenuHandlers() {
    const setupHandlers = () => {
      const menuItems = document.querySelectorAll("#dropdown-menu .menu-item[data-action]");
      console.log(
        "Setting up menu menu handlers for",
        menuItems.length,
        "items"
      );

      if (menuItems.length === 0) {
        console.warn("No menu items found! Retrying...");
        setTimeout(setupHandlers, 200);
        return;
      }

      menuItems.forEach((item) => {
        item.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          const action = item.getAttribute("data-action");
          console.log("Menu menu action clicked:", action);
          this.handleMenuMenuAction(action);
          this.manager.hideMenuMenu();
        });
      });
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupHandlers);
    } else {
      setupHandlers();
    }
  }

  handleMenuMenuAction(action) {
    switch (action) {
      case "open-settings":
        this.manager.updateStatus("Opening settings.yml file...");
        this.manager.openSettingsFile();
        break;
      case "open-apps-config":
        this.manager.updateStatus("Opening loaded_apps.yml file...");
        this.manager.openAppsConfigFile();
        break;
      case "open-load-apps-config":
        this.manager.updateStatus("Opening load_apps.yml file...");
        this.manager.openLoadAppsConfigFile();
        break;
      case "reload-config":
        this.manager.reloadConfiguration();
        break;
      case "about":
        this.manager.updateStatus("Opening about dialog...");
        this.manager.showAbout();
        break;
      default:
        this.manager.updateStatus(`Menu menu action: ${action}`);
    }
  }
}
