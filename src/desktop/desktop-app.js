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
 * Desktop Application - Modular architecture with separated concerns
 */

import { ConfigManager } from './modules/config.js';
import { ThemeManager } from './modules/theme.js';
import { UIManager } from './modules/ui.js';
import { AppsManager } from './modules/apps.js';
import { OperationsManager } from './modules/operations.js';
import { LoadAppsManager } from './modules/load-apps.js';
import { ProfilesManager } from './modules/profiles.js';
import { OnboardingManager } from './modules/onboarding.js';
import { EventsManager } from './modules/events.js';

const APP_VERSION = '0.1.0';

class DesktopAppManager {
  constructor() {
    this.APP_VERSION = APP_VERSION;
    this.apps = [];
    this.activeApps = [];
    this.selectedApps = new Set();
    this.currentTheme = "dark";
    this.isLoading = false;
    this.appConfig = null;
    this.availableApps = null;
    this.refreshInterval = null;
    this.currentOnboardingStep = 1;
    this.onboardingListenersSetup = false;

    this.configManager = new ConfigManager(this);
    this.themeManager = new ThemeManager(this);
    this.uiManager = new UIManager(this);
    this.appsManager = new AppsManager(this);
    this.operationsManager = new OperationsManager(this);
    this.loadAppsManager = new LoadAppsManager(this);
    this.profilesManager = new ProfilesManager(this);
    this.onboardingManager = new OnboardingManager(this);
    this.eventsManager = new EventsManager(this);

    this.init();
  }

  async init() {
    try {
      console.log("Initializing Desktop App Manager...");

      await this.loadConfiguration();
      console.log("Configuration loaded, setting up UI...");

      this.applyGridLayout();

      this.setupEventListeners();
      this.renderAppGrid();
      this.updateSelectedApps();
      this.updateStatus(`Ready - Loaded ${this.apps.length} apps from config`);
      this.refreshActiveApps();
      this.initializeTheme();

      this.startPeriodicRefresh();

      this.updateAppTitle();

      const currentMode = this.appConfig?.window?.layout_mode || "grid";
      this.updateLayoutModeUI(currentMode);

      await this.loadAllAvailableApps();

      console.log(
        "Desktop App Manager initialized with Load Apps panel as default"
      );

      setTimeout(() => {
        this.checkFirstTimeLaunch();
      }, 500);
    } catch (error) {
      console.error("Failed to initialize App Manager:", error);
      console.error("Error details:", error.stack);
      this.updateStatus("Error loading configuration");
    }
  }

  async electronAPI(method, ...args) {
    try {
      if (window.electronAPI && window.electronAPI[method]) {
        return await window.electronAPI[method](...args);
      } else {
        throw new Error(`Electron API method ${method} not available`);
      }
    } catch (error) {
      console.error(`Electron API error (${method}):`, error);
      throw error;
    }
  }

  loadConfiguration() { return this.configManager.loadConfiguration(); }
  applyGridLayout() { return this.configManager.applyGridLayout(); }
  reloadConfiguration() { return this.configManager.reloadConfiguration(); }
  reloadConfigurationAndUI() { return this.configManager.reloadConfigurationAndUI(); }
  updateAppTitle() { return this.configManager.updateAppTitle(); }

  initializeTheme() { return this.themeManager.initializeTheme(); }
  toggleTheme() { return this.themeManager.toggleTheme(); }
  setTheme(theme) { return this.themeManager.setTheme(theme); }

  updateStatus(message) { return this.uiManager.updateStatus(message); }
  setLoading(loading) { return this.uiManager.setLoading(loading); }
  showHelpModal() { return this.uiManager.showHelpModal(); }
  hideHelpModal() { return this.uiManager.hideHelpModal(); }
  showSettings() { return this.uiManager.showSettings(); }
  showAbout() { return this.uiManager.showAbout(); }
  toggleLeftPanel() { return this.uiManager.toggleLeftPanel(); }
  expandLeftPanel() { return this.uiManager.expandLeftPanel(); }
  toggleMenuMenu() { return this.uiManager.toggleMenuMenu(); }
  showMenuMenu() { return this.uiManager.showMenuMenu(); }
  hideMenuMenu() { return this.uiManager.hideMenuMenu(); }
  showContextMenu(event) { return this.uiManager.showContextMenu(event); }
  hideContextMenu() { return this.uiManager.hideContextMenu(); }
  updateLayoutModeUI(mode) { return this.uiManager.updateLayoutModeUI(mode); }
  openSettingsFile() { return this.uiManager.openSettingsFile(); }
  openAppsConfigFile() { return this.uiManager.openAppsConfigFile(); }
  openLoadAppsConfigFile() { return this.uiManager.openLoadAppsConfigFile(); }

  updateSelectedApps() { return this.appsManager.updateSelectedApps(); }
  renderAppGrid() { return this.appsManager.renderAppGrid(); }
  renderAppGridOptimized() { return this.appsManager.renderAppGridOptimized(); }
  getAppStatus(appName) { return this.appsManager.getAppStatus(appName); }
  toggleAppSelection(appId, selected) { return this.appsManager.toggleAppSelection(appId, selected); }
  selectAllApps() { return this.appsManager.selectAllApps(); }
  clearSelection() { return this.appsManager.clearSelection(); }
  setupDragAndDrop() { return this.appsManager.setupDragAndDrop(); }
  getDragAfterElement(container, y) { return this.appsManager.getDragAfterElement(container, y); }
  updatePrioritiesFromDOM() { return this.appsManager.updatePrioritiesFromDOM(); }
  savePriorityOrder() { return this.appsManager.savePriorityOrder(); }
  refreshActiveApps() { return this.appsManager.refreshActiveApps(); }
  startPeriodicRefresh() { return this.appsManager.startPeriodicRefresh(); }
  stopPeriodicRefresh() { return this.appsManager.stopPeriodicRefresh(); }

  startApps() { return this.operationsManager.startApps(); }
  autoUnloadAfterStart() { return this.operationsManager.autoUnloadAfterStart(); }
  arrangeGrid() { return this.operationsManager.arrangeGrid(); }
  toggleLayoutMode() { return this.operationsManager.toggleLayoutMode(); }
  minimizeAll() { return this.operationsManager.minimizeAll(); }
  closeAllApps() { return this.operationsManager.closeAllApps(); }
  reopenAllApps() { return this.operationsManager.reopenAllApps(); }
  refreshAllApps() { return this.operationsManager.refreshAllApps(); }

  loadAllAvailableApps() { return this.loadAppsManager.loadAllAvailableApps(); }
  renderAppsTable(desktopApplications) { return this.loadAppsManager.renderAppsTable(desktopApplications); }
  populateProfileDropdown(desktopApplications) { return this.loadAppsManager.populateProfileDropdown(desktopApplications); }
  renderEmptyAppsTable(message) { return this.loadAppsManager.renderEmptyAppsTable(message); }
  setupAppsTableEventListeners() { return this.loadAppsManager.setupAppsTableEventListeners(); }
  loadAllAppsForSelectedProfile() { return this.loadAppsManager.loadAllAppsForSelectedProfile(); }

  loadSingleProfile(appName, profileName, appPath) { return this.profilesManager.loadSingleProfile(appName, profileName, appPath); }
  unloadProfile(appName, profileName) { return this.profilesManager.unloadProfile(appName, profileName); }
  unloadAllApps() { return this.profilesManager.unloadAllApps(); }
  unloadSelectedApps() { return this.profilesManager.unloadSelectedApps(); }

  checkFirstTimeLaunch() { return this.onboardingManager.checkFirstTimeLaunch(); }
  showOnboarding() { return this.onboardingManager.showOnboarding(); }
  hideOnboarding() { return this.onboardingManager.hideOnboarding(); }
  setupOnboardingEventListeners() { return this.onboardingManager.setupOnboardingEventListeners(); }
  nextOnboardingStep() { return this.onboardingManager.nextOnboardingStep(); }
  updateOnboardingStep(step) { return this.onboardingManager.updateOnboardingStep(step); }
  highlightThreeDotMenu() { return this.onboardingManager.highlightThreeDotMenu(); }
  resetOnboarding() { return this.onboardingManager.resetOnboarding(); }
  resetAndShow() { return this.onboardingManager.resetAndShow(); }
  forceShowOnboarding() { return this.onboardingManager.forceShowOnboarding(); }
  completeOnboarding() { return this.onboardingManager.completeOnboarding(); }

  setupEventListeners() { return this.eventsManager.setupEventListeners(); }
  setupMenuMenuHandlers() { return this.eventsManager.setupMenuMenuHandlers(); }
  handleMenuMenuAction(action) { return this.eventsManager.handleMenuMenuAction(action); }
}

document.addEventListener("DOMContentLoaded", () => {
  window.appManager = new DesktopAppManager();
});

window.addEventListener("focus", () => {
  if (window.appManager) {
    window.appManager.refreshActiveApps();
  }
});

window.addEventListener("beforeunload", () => {
  if (window.appManager) {
    window.appManager.stopPeriodicRefresh();
  }
});

console.log("SpectraTact loaded");
