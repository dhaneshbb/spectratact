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
 * Onboarding Module
 */

export class OnboardingManager {
  constructor(manager) {
    this.manager = manager;
  }

  checkFirstTimeLaunch() {
    const hasCompletedOnboarding = localStorage.getItem(
      "desktopApp_onboarding_completed"
    );
    const onboardingDate = localStorage.getItem("desktopApp_onboarding_date");
    const onboardingVersion = localStorage.getItem("desktopApp_onboarding_version");
    const currentVersion = this.manager.APP_VERSION;

    console.log("Checking first time launch...");
    console.log("Has completed onboarding:", hasCompletedOnboarding);
    console.log("Onboarding date:", onboardingDate);
    console.log("Onboarding version:", onboardingVersion);
    console.log("Current version:", currentVersion);
    console.log("localStorage keys:", Object.keys(localStorage));

    const needsOnboarding =
      !hasCompletedOnboarding ||
      hasCompletedOnboarding === "false" ||
      onboardingVersion !== currentVersion;

    if (needsOnboarding) {
      if (onboardingVersion !== currentVersion) {
        console.log(
          "App version changed, showing onboarding for new features/structure"
        );
      } else {
        console.log(
          "First time launch detected, showing onboarding in 2 seconds"
        );
      }
      setTimeout(() => {
        this.showOnboarding();
      }, 2000);
    } else {
      console.log("Onboarding already completed, skipping");
    }
  }

  showOnboarding() {
    console.log("Attempting to show onboarding modal...");
    const modal = document.getElementById("onboarding-modal");

    if (modal) {
      console.log("Onboarding modal found, showing...");

      modal.style.display = "flex";
      modal.style.opacity = "1";
      modal.style.visibility = "visible";
      modal.classList.add("show");

      this.setupOnboardingEventListeners();
      this.manager.currentOnboardingStep = 1;
      this.updateOnboardingStep(1);

      console.log("Onboarding modal should now be visible");
      console.log("Modal computed styles:", {
        display: getComputedStyle(modal).display,
        opacity: getComputedStyle(modal).opacity,
        visibility: getComputedStyle(modal).visibility,
        zIndex: getComputedStyle(modal).zIndex,
      });
    } else {
      console.error("Onboarding modal not found in DOM!");
      console.log(
        "Available elements with IDs:",
        Array.from(document.querySelectorAll("[id]")).map((el) => el.id)
      );
    }
  }

  hideOnboarding() {
    console.log("Hiding onboarding modal...");
    const modal = document.getElementById("onboarding-modal");
    if (modal) {
      modal.classList.remove("show");
      modal.style.display = "none";
      modal.style.opacity = "0";
      modal.style.visibility = "hidden";

      localStorage.setItem("desktopApp_onboarding_completed", "true");
      localStorage.setItem("desktopApp_onboarding_date", new Date().toISOString());
      localStorage.setItem("desktopApp_onboarding_version", this.manager.APP_VERSION);

      this.manager.onboardingListenersSetup = false;

      console.log("Onboarding modal hidden and marked as completed");
    }
  }

  setupOnboardingEventListeners() {
    console.log("Setting up onboarding event listeners...");

    if (this.manager.onboardingListenersSetup) {
      console.log("Onboarding listeners already set up, skipping...");
      return;
    }
    this.manager.onboardingListenersSetup = true;

    const skipBtn = document.getElementById("skip-onboarding");
    const completeBtn = document.getElementById("complete-setup");
    const settingsBtn = document.getElementById("open-settings-setup");
    const appsBtn = document.getElementById("open-apps-setup");

    console.log("Button debug:", {
      skipBtn: !!skipBtn,
      completeBtn: !!completeBtn,
      settingsBtn: !!settingsBtn,
      appsBtn: !!appsBtn,
    });

    document
      .getElementById("open-settings-setup")
      ?.addEventListener("click", async () => {
        console.log(
          "Settings button clicked, current step before:",
          this.manager.currentOnboardingStep
        );
        try {
          await window.electronAPI.openSettings();
          console.log(
            "Settings file opened successfully, calling nextOnboardingStep..."
          );
          this.nextOnboardingStep();
        } catch (error) {
          console.error("Failed to open settings:", error);
        }
      });

    document
      .getElementById("open-apps-setup")
      ?.addEventListener("click", async () => {
        try {
          await this.manager.openLoadAppsConfigFile();
          this.nextOnboardingStep();
        } catch (error) {
          console.error("Failed to open load apps config:", error);
        }
      });

    document.getElementById("next-step-1")?.addEventListener("click", () => {
      console.log("Next step 1 clicked");
      this.nextOnboardingStep();
    });
    document.getElementById("next-step-2")?.addEventListener("click", () => {
      console.log("Next step 2 clicked");
      this.nextOnboardingStep();
    });
    document.getElementById("complete-setup")?.addEventListener("click", () => {
      console.log("Complete setup clicked");
      this.completeOnboarding();
    });
    document
      .getElementById("skip-onboarding")
      ?.addEventListener("click", () => {
        console.log("Skip onboarding clicked");
        this.hideOnboarding();
      });

    if (this.manager.currentOnboardingStep === 3) {
      this.highlightThreeDotMenu();
    }
  }

  nextOnboardingStep() {
    console.log(
      "nextOnboardingStep called, current step:",
      this.manager.currentOnboardingStep
    );
    this.manager.currentOnboardingStep++;
    console.log("Moving to step:", this.manager.currentOnboardingStep);

    if (this.manager.currentOnboardingStep <= 3) {
      this.updateOnboardingStep(this.manager.currentOnboardingStep);

      if (this.manager.currentOnboardingStep === 3) {
        this.highlightThreeDotMenu();
      }
    } else {
      this.completeOnboarding();
    }
  }

  updateOnboardingStep(step) {
    console.log("updateOnboardingStep called with step:", step);

    document.querySelectorAll(".onboarding-step").forEach((stepEl) => {
      stepEl.classList.remove("active");
    });

    const currentStepEl = document.querySelector(`[data-step="${step}"]`);
    console.log("Found step element:", !!currentStepEl, "for step:", step);
    if (currentStepEl) {
      currentStepEl.classList.add("active");
    }

    document.querySelectorAll(".step-indicator").forEach((indicator, index) => {
      if (index + 1 <= step) {
        indicator.classList.add("active");
      } else {
        indicator.classList.remove("active");
      }
    });

    console.log("Step update complete for step:", step);
  }

  highlightThreeDotMenu() {
    const menuBtn = document.getElementById("menu-btn-dropdown");
    if (menuBtn) {
      menuBtn.classList.add("highlight");

      setTimeout(() => {
        menuBtn.classList.remove("highlight");
      }, 10000);
    }
  }

  resetOnboarding() {
    localStorage.removeItem("desktopApp_onboarding_completed");
    localStorage.removeItem("desktopApp_onboarding_date");
    localStorage.removeItem("desktopApp_onboarding_version");
    console.log("Onboarding reset - will show on next launch");
  }

  resetAndShow() {
    this.resetOnboarding();
    console.log("Showing onboarding immediately after reset...");
    setTimeout(() => {
      this.showOnboarding();
    }, 100);
  }

  forceShowOnboarding() {
    console.log("Forcing onboarding to show...");
    this.showOnboarding();
  }

  completeOnboarding() {
    this.hideOnboarding();

    this.manager.updateStatus(
      "Welcome! You can access settings anytime through the three-dot menu (⋮)"
    );

    const menuBtn = document.getElementById("menu-btn-dropdown");
    if (menuBtn) {
      menuBtn.classList.remove("highlight");
    }
  }
}
