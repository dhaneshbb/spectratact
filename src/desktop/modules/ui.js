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
 * UI Utilities Module
 */

export class UIManager {
  constructor(manager) {
    this.manager = manager;
  }

  updateStatus(message) {
    document.getElementById("status-display").textContent = message;
  }

  setLoading(loading) {
    this.manager.isLoading = loading;

    const buttons = document.querySelectorAll(".toolbar-btn, .action-btn");
    buttons.forEach((btn) => {
      if (loading) {
        btn.style.opacity = "0.6";
        btn.style.pointerEvents = "none";
      } else {
        btn.style.opacity = "";
        btn.style.pointerEvents = "";
      }
    });
  }

  showHelpModal() {
    document.getElementById("help-modal").classList.add("show");
  }

  hideHelpModal() {
    document.getElementById("help-modal").classList.remove("show");
  }

  showSettings() {
    this.updateStatus("Settings panel coming soon");
  }

  showAbout() {
    this.updateStatus(`SpectraTact v${this.manager.APP_VERSION}`);
  }

  toggleLeftPanel() {
    const leftPanel = document.getElementById("left-panel");
    const collapsedHeader = document.getElementById("collapsed-panel-header");
    const isCollapsed = leftPanel.classList.contains("collapsed");

    if (isCollapsed) {
      leftPanel.classList.remove("collapsed");
      collapsedHeader.style.display = "none";
      this.updateStatus("Applications panel expanded");
    } else {
      leftPanel.classList.add("collapsed");
      collapsedHeader.style.display = "flex";
      this.updateStatus("Applications panel collapsed");
    }
  }

  expandLeftPanel() {
    const leftPanel = document.getElementById("left-panel");
    const collapsedHeader = document.getElementById("collapsed-panel-header");

    leftPanel.classList.remove("collapsed");
    collapsedHeader.style.display = "none";
    this.updateStatus("Applications panel expanded");
  }

  toggleMenuMenu() {
    const menu = document.getElementById("dropdown-menu");
    console.log("toggleMenuMenu called, menu element:", menu);

    if (!menu) {
      console.error("Dropdown menu element not found!");
      return;
    }

    const isVisible = menu.classList.contains("show");
    console.log("Menu is currently visible:", isVisible);

    if (isVisible) {
      this.hideMenuMenu();
    } else {
      this.showMenuMenu();
    }
  }

  showMenuMenu() {
    const menu = document.getElementById("dropdown-menu");
    console.log("showMenuMenu called, adding 'show' class");
    menu.classList.add("show");
    console.log("Menu classes after show:", menu.className);
    this.hideContextMenu();
  }

  hideMenuMenu() {
    const menu = document.getElementById("dropdown-menu");
    menu.classList.remove("show");
  }

  showContextMenu(event) {
    const menu = document.getElementById("context-menu");
    const rect = event.target.getBoundingClientRect();

    menu.style.left = `${rect.left}px`;
    menu.style.top = `${rect.bottom + 5}px`;
    menu.classList.add("show");

    menu.querySelectorAll(".menu-item").forEach((item) => {
      item.onclick = () => {
        const action = item.getAttribute("data-action");
        this.handleMenuAction(action);
        this.hideContextMenu();
      };
    });
  }

  hideContextMenu() {
    document.getElementById("context-menu").classList.remove("show");
  }

  handleMenuAction(action) {
    switch (action) {
      case "close-all":
        this.manager.closeAllApps();
        break;
      case "reopen-all":
        this.manager.reopenAllApps();
        break;
      case "settings":
        this.showSettings();
        break;
      case "about":
        this.showAbout();
        break;
    }
  }

  updateLayoutModeUI(mode) {
    const button = document.getElementById("layout-mode-btn");
    const textElement = document.getElementById("layout-mode-text");
    const svg = button.querySelector("svg path");

    if (mode === "grid") {
      textElement.textContent = "Grid";
      button.title = "Toggle Layout Mode (Currently: Grid → Side-by-Side)";
      svg.setAttribute(
        "d",
        "M3 3h8v8H3zM13 3h8v8h-8zM3 13h8v8H3zM13 13h8v8h-8z"
      );
    } else {
      textElement.textContent = "Side";
      button.title = "Toggle Layout Mode (Currently: Side-by-Side → Grid)";
      svg.setAttribute("d", "M3 3h18v5H3zM3 10h8v11H3zM13 10h8v11h-8z");
    }

    button.style.backgroundColor = "var(--accent-color)";
    setTimeout(() => {
      button.style.backgroundColor = "";
    }, 300);
  }

  async openSettingsFile() {
    try {
      const result = await this.manager.electronAPI("openFile", "settings.yml");
      if (result.success) {
        this.updateStatus("settings.yml opened in default editor");
      } else {
        this.updateStatus("Failed to open settings.yml: " + result.error);
      }
    } catch (error) {
      console.error("Error opening settings file:", error);
      this.updateStatus("Error opening settings.yml file");
    }
  }

  async openAppsConfigFile() {
    try {
      const result = await this.manager.electronAPI("openFile", "loaded_apps.yml");
      if (result.success) {
        this.updateStatus("loaded_apps.yml opened in default editor");
      } else {
        this.updateStatus("Failed to open loaded_apps.yml: " + result.error);
      }
    } catch (error) {
      console.error("Error opening apps config file:", error);
      this.updateStatus("Error opening loaded_apps.yml file");
    }
  }

  async openLoadAppsConfigFile() {
    try {
      const result = await this.manager.electronAPI("openFile", "load_apps.yml");
      if (result.success) {
        this.updateStatus("load_apps.yml opened in default editor");
      } else {
        this.updateStatus("Failed to open load_apps.yml: " + result.error);
      }
    } catch (error) {
      console.error("Error opening load apps config file:", error);
      this.updateStatus("Error opening load_apps.yml file");
    }
  }
}
