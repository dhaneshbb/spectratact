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
 * Theme Management Module
 */

export class ThemeManager {
  constructor(manager) {
    this.manager = manager;
  }

  initializeTheme() {
    this.applyConfigTheme();

    const savedTheme = localStorage.getItem("theme") || "dark";
    this.setTheme(savedTheme);
  }

  applyConfigTheme() {
    if (this.manager.appConfig && this.manager.appConfig.gui && this.manager.appConfig.gui.theme) {
      const theme = this.manager.appConfig.gui.theme;

      const root = document.documentElement;

      if (theme.bg_primary)
        root.style.setProperty("--bg-primary", theme.bg_primary);
      if (theme.bg_secondary)
        root.style.setProperty("--bg-secondary", theme.bg_secondary);
      if (theme.bg_input) root.style.setProperty("--bg-input", theme.bg_input);
      if (theme.fg_primary)
        root.style.setProperty("--text-primary", theme.fg_primary);
      if (theme.fg_secondary)
        root.style.setProperty("--text-secondary", theme.fg_secondary);
      if (theme.accent_color)
        root.style.setProperty("--accent-primary", theme.accent_color);
      if (theme.success_color)
        root.style.setProperty("--accent-success", theme.success_color);
      if (theme.warning_color)
        root.style.setProperty("--accent-warning", theme.warning_color);
      if (theme.error_color)
        root.style.setProperty("--accent-error", theme.error_color);

      console.log("Applied theme colors from config:", theme);
    }

    if (this.manager.appConfig && this.manager.appConfig.gui && this.manager.appConfig.gui.fonts) {
      const fonts = this.manager.appConfig.gui.fonts;
      const root = document.documentElement;

      if (fonts.normal && Array.isArray(fonts.normal)) {
        const fontFamily = fonts.normal[0];
        const fontSize = fonts.normal[1] ? `${fonts.normal[1]}px` : "11px";
        root.style.setProperty(
          "--font-system",
          `"${fontFamily}", -apple-system, BlinkMacSystemFont, sans-serif`
        );
        root.style.setProperty("--font-size-normal", fontSize);
      }

      if (fonts.title && Array.isArray(fonts.title)) {
        const fontFamily = fonts.title[0];
        const fontSize = fonts.title[1] ? `${fonts.title[1]}px` : "16px";
        const fontWeight = fonts.title[2] || "bold";
        root.style.setProperty(
          "--font-title-family",
          `"${fontFamily}", -apple-system, BlinkMacSystemFont, sans-serif`
        );
        root.style.setProperty("--font-title-size", fontSize);
        root.style.setProperty("--font-title-weight", fontWeight);
      }

      console.log("Applied fonts from config:", fonts);
    }
  }

  toggleTheme() {
    const newTheme = this.manager.currentTheme === "dark" ? "light" : "dark";
    this.setTheme(newTheme);
  }

  setTheme(theme) {
    this.manager.currentTheme = theme;
    document.querySelector(".app-container").setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);

    const sunIcon = document.querySelector(".sun-icon");
    const moonIcon = document.querySelector(".moon-icon");

    if (theme === "light") {
      sunIcon.style.display = "none";
      moonIcon.style.display = "block";
    } else {
      sunIcon.style.display = "block";
      moonIcon.style.display = "none";
    }
  }
}
