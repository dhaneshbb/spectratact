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
 *
 * App Grid Management Module
 */

export class AppsManager {
  constructor(manager) {
    this.manager = manager;
  }

  updateSelectedApps() {
    this.manager.selectedApps.clear();
    this.manager.apps.forEach((app) => {
      if (app.selected) {
        this.manager.selectedApps.add(app.name);
      }
    });
  }

  renderAppGrid() {
    const grid = document.getElementById("app-grid");

    grid.innerHTML = "";

    this.manager.apps.forEach((app, index) => {
      const card = document.createElement("div");
      card.className = "app-card";
      card.setAttribute("data-app", app.name);
      card.setAttribute("data-priority", app.priority || index + 1);

      card.draggable = true;
      card.setAttribute("draggable", "true");

      if (app.selected) {
        card.classList.add("selected");
      }

      if (!app.enabled) {
        card.classList.add("disabled");
      }

      card.innerHTML = `
        <div class="app-info">
          <span class="app-name">${app.name}</span>
          <span class="app-status">${this.getAppStatus(app.name)}</span>
        </div>
        <div class="app-controls">
          <input type="checkbox" class="app-checkbox" id="${app.id}-check" ${app.selected ? "checked" : ""}>
        </div>
      `;

      const checkbox = card.querySelector(".app-checkbox");

      card.addEventListener("click", (e) => {
        if (e.target.type !== "checkbox") {
          checkbox.checked = !checkbox.checked;
          this.toggleAppSelection(app.id, checkbox.checked);
        }
      });

      checkbox.addEventListener("change", (e) => {
        e.stopPropagation();
        this.toggleAppSelection(app.id, e.target.checked);
      });

      grid.appendChild(card);
    });

    console.log(
      "App grid rendered with",
      this.manager.apps.length,
      "apps in priority order"
    );
  }

  renderAppGridOptimized() {
    const cards = document.querySelectorAll(".app-card");

    cards.forEach((card) => {
      const appName = card.getAttribute("data-app");
      const statusElement = card.querySelector(".app-status");

      if (statusElement) {
        const activeApp = this.manager.activeApps.find((app) => app.name === appName);
        const newStatus = activeApp
          ? activeApp.is_minimized
            ? "Minimized"
            : "Active"
          : "Not Started";

        if (statusElement.textContent !== newStatus) {
          statusElement.textContent = newStatus;
        }
      }
    });
  }

  getAppStatus(appName) {
    const activeApp = this.manager.activeApps.find((app) => app.name === appName);
    if (activeApp) {
      return activeApp.is_minimized ? "Minimized" : "Active";
    }
    return "Not Started";
  }

  toggleAppSelection(appId, selected) {
    const app = this.manager.apps.find((a) => a.id === appId);
    if (app) {
      app.selected = selected;
      if (selected) {
        this.manager.selectedApps.add(app.name);
      } else {
        this.manager.selectedApps.delete(app.name);
      }

      const card = document.querySelector(`[data-app="${app.name}"]`);
      card.classList.toggle("selected", selected);
    }
  }

  selectAllApps() {
    this.manager.apps.forEach((app) => {
      app.selected = true;
      this.manager.selectedApps.add(app.name);

      const card = document.querySelector(`[data-app="${app.name}"]`);
      const checkbox = card.querySelector(".app-checkbox");
      checkbox.checked = true;
      card.classList.add("selected");
    });
  }

  clearSelection() {
    this.manager.apps.forEach((app) => {
      app.selected = false;
      this.manager.selectedApps.delete(app.name);

      const card = document.querySelector(`[data-app="${app.name}"]`);
      const checkbox = card.querySelector(".app-checkbox");
      checkbox.checked = false;
      card.classList.remove("selected");
    });
  }

  setupDragAndDrop() {
    const grid = document.getElementById("app-grid");
    let draggedElement = null;
    let placeholder = null;

    const createPlaceholder = () => {
      const placeholder = document.createElement("div");
      placeholder.className = "app-card-placeholder";
      placeholder.innerHTML = `
        <div class="placeholder-content">
          <div class="placeholder-icon">⋮⋮</div>
          <span>Drop here to reorder</span>
        </div>
      `;
      return placeholder;
    };

    grid.addEventListener("dragstart", (e) => {
      if (e.target.classList.contains("app-card")) {
        draggedElement = e.target;
        e.target.classList.add("dragging");
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/html", e.target.outerHTML);

        placeholder = createPlaceholder();
        setTimeout(() => {
          e.target.style.display = "none";
          e.target.parentNode.insertBefore(placeholder, e.target);
        }, 0);
      }
    });

    grid.addEventListener("dragend", (e) => {
      if (e.target.classList.contains("app-card")) {
        e.target.classList.remove("dragging");
        e.target.style.display = "";

        if (placeholder && placeholder.parentNode) {
          placeholder.parentNode.removeChild(placeholder);
        }
        placeholder = null;
        draggedElement = null;
      }
    });

    grid.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";

      const afterElement = this.getDragAfterElement(grid, e.clientY);
      if (afterElement == null) {
        if (placeholder) {
          grid.appendChild(placeholder);
        }
      } else {
        if (placeholder) {
          grid.insertBefore(placeholder, afterElement);
        }
      }
    });

    grid.addEventListener("drop", (e) => {
      e.preventDefault();

      if (draggedElement && placeholder) {
        placeholder.parentNode.insertBefore(draggedElement, placeholder);
        placeholder.parentNode.removeChild(placeholder);

        this.updatePrioritiesFromDOM();
        this.savePriorityOrder();

        console.log("Applications reordered by drag and drop");
      }
    });
  }

  getDragAfterElement(container, y) {
    const draggableElements = [
      ...container.querySelectorAll(".app-card:not(.dragging)"),
    ];

    return draggableElements.reduce(
      (closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
          return { offset: offset, element: child };
        } else {
          return closest;
        }
      },
      { offset: Number.NEGATIVE_INFINITY }
    ).element;
  }

  updatePrioritiesFromDOM() {
    const cards = document.querySelectorAll(".app-card");
    cards.forEach((card, index) => {
      const appName = card.getAttribute("data-app");
      const app = this.manager.apps.find((a) => a.name === appName);
      if (app) {
        app.priority = index + 1;
        card.setAttribute("data-priority", app.priority);
      }
    });

    this.manager.apps.sort((a, b) => (a.priority || 999) - (b.priority || 999));
  }

  async savePriorityOrder() {
    try {
      const priorityUpdate = {};
      this.manager.apps.forEach((app, index) => {
        priorityUpdate[app.name] = index + 1;
      });

      await this.manager.electronAPI("updatePriorities", priorityUpdate);

      this.manager.updateStatus("Priority order saved successfully");
    } catch (error) {
      console.error("Failed to save priority order:", error);
      this.manager.updateStatus("Error saving priority order");
    }
  }

  async refreshActiveApps(forceRefresh = false) {
    try {
      // If force refresh, append timestamp to bypass cache
      const method = forceRefresh ? "getActiveApps" : "getActiveApps";
      const params = forceRefresh ? { _cache_bust: Date.now() } : undefined;

      const result = await this.manager.electronAPI(method, params);
      const newActiveApps = Array.isArray(result) ? result : [];

      // More granular change detection - check if any app's status changed
      const hasChanges =
        !this.manager.activeApps ||
        this.manager.activeApps.length !== newActiveApps.length ||
        this._hasAppStatusChanges(this.manager.activeApps, newActiveApps);

      if (!hasChanges) {
        return;
      }

      this.manager.activeApps = newActiveApps;

      const statusIndicator = document.getElementById("status-indicator");
      const statusText = document.getElementById("status-text");

      if (this.manager.activeApps.length > 0) {
        if (!statusIndicator.classList.contains("connected")) {
          statusIndicator.classList.add("connected");
        }
        statusText.textContent = `${this.manager.activeApps.length} apps running`;
      } else {
        statusIndicator.classList.remove("connected");
        statusText.textContent = "No apps running";
      }

      this.renderAppGridOptimized();
    } catch (error) {
      console.error("Error refreshing app status:", error);
    }
  }

  _hasAppStatusChanges(oldApps, newApps) {
    if (!oldApps || !newApps) return true;
    if (oldApps.length !== newApps.length) return true;

    // Check if any app's minimized status changed
    for (let i = 0; i < oldApps.length; i++) {
      const oldApp = oldApps[i];
      const newApp = newApps.find(a => a.name === oldApp.name);

      if (!newApp) return true;
      if (oldApp.is_minimized !== newApp.is_minimized) return true;
      if (oldApp.hwnd !== newApp.hwnd) return true;
    }

    return false;
  }

  startPeriodicRefresh() {
    if (this.manager.refreshInterval) {
      clearInterval(this.manager.refreshInterval);
    }

    // Get polling interval from config (default 3000ms)
    const pollingInterval = this.manager.appConfig?.performance?.ui_updates?.polling_interval || 3000;

    this.manager.refreshInterval = setInterval(() => {
      this.refreshActiveApps();
    }, pollingInterval);

    console.log(`Started periodic app stats refresh (every ${pollingInterval}ms)`);
  }

  stopPeriodicRefresh() {
    if (this.manager.refreshInterval) {
      clearInterval(this.manager.refreshInterval);
      this.manager.refreshInterval = null;
      console.log("Stopped periodic app stats refresh");
    }
  }
}
