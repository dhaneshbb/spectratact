# Configuration Guide

SpectraTact uses three YAML configuration files for application behavior and profile management.

## Table of Contents

- [Configuration Files](#configuration-files)
- [settings.yml](#settingsyml)
  - [Layout Modes](#layout-modes)
  - [Display Configuration](#display-configuration)
  - [Timing Configuration](#timing-configuration)
  - [GUI Configuration](#gui-configuration)
  - [Security Configuration](#security-configuration)
  - [Communication Settings](#communication-settings)
  - [Performance Configuration](#performance-configuration)
- [loaded_apps.yml](#loaded_appsyml)
- [load_apps.yml](#load_appsyml)
- [Configuration Validation](#configuration-validation)
- [Live Reload](#live-reload)
- [See Also](#see-also)

## Configuration Files

**config/settings.yml** - Application behavior
- Window layout mode (grid or side-by-side)
- Display and timing configuration
- GUI theme and appearance
- Performance and caching
- Security settings

**config/loaded_apps.yml** - Active profiles
- Applications launched on "Start Apps"
- Priority-based arrangement order
- Managed via GUI or manual editing

**config/load_apps.yml** - Profile library
- Master list of available application profiles
- Keywords for window detection
- Source for loading into loaded_apps.yml

## settings.yml

### Layout Modes

**Grid Layout:**
```yaml
window:
  layout_mode: grid
  grid:
    cols: 5
    rows: 2
```
Arranges windows in NxM matrix (5x2 = 10 windows). Validator limits: cols/rows 1-6, warns if total > 12.

**Side-by-Side Layout:**
```yaml
window:
  layout_mode: side_by_side
  side_by_side:
    orientation: horizontal  # or vertical
    split_ratio: 0.5         # Range: 0.0-1.0 (exclusive)
    max_windows: 9           # Range: 2-10
```

### Display Configuration

```yaml
window:
  display:
    auto_select: false
    preferred_display: "2"           # "1", "1,2", "auto"
    use_work_area: true              # Respect taskbar
    multi_display_mode: primary_overflow  # span, distribute, primary_overflow
```

### Timing Configuration

```yaml
window:
  timing:
    launch_delay: 0.1    # Range: 0.0-5.0 seconds
    load_wait: 4.0       # Range: 0.5-30.0 seconds
    action_delay: 0.1    # Range: 0.0-2.0 seconds
```

### GUI Configuration

```yaml
gui:
  theme:
    bg_primary: "#1e1e1e"    # Hex color format
    fg_primary: "#ffffff"
    accent_color: "#0078d4"
    success_color: "#4CAF50"
    warning_color: "#FF9800"
    error_color: "#f44336"

  window:
    width: 1000              # Range: 300-3000 pixels
    height: 700              # Range: 300-3000 pixels
    always_on_top: true
    resizable: true

  fonts:
    title: ["Segoe UI", 16, "bold"]
    normal: ["Segoe UI", 11]
    small: ["Segoe UI", 9]
    button: ["Segoe UI", 10]
```

### Security Configuration

```yaml
security:
  app_access:
    allow_unknown_apps: false
  system:
    window_management: true

taskbar:
  hide_apps: true

target_detection:
  target_only: true
  valid_executables:
    - "chrome.exe"
    - "Code.exe"
```

### Communication Settings

```yaml
communication:
  cache_ttl: 1000              # Milliseconds
  refresh_delay: 300           # Milliseconds

  timeouts:
    default: 8000              # Range: 1000-60000 ms
    start_apps: 25000          # Range: 5000-120000 ms
    refresh_all_pages: 15000   # Range: 3000-30000 ms
    websocket_connection: 2    # Range: 1-30 seconds
    subprocess: 5              # Range: 1-60 seconds
    electron_bridge: 25        # Range: 5-120 seconds
```

### Performance Configuration

```yaml
performance:
  backend_cache:
    enabled: true
    ttl: 1500                  # Range: 0-10000 ms
    max_age: 3000              # Range: 0-30000 ms

  frontend_cache:
    enabled: true
    ttl: 1000                  # Range: 0-10000 ms
    max_entries: 15            # Range: 1-100

  ui_updates:
    optimistic_updates: true
    polling_interval: 3000     # Range: 1000-30000 ms
    immediate_refresh_delay: 50  # Range: 0-1000 ms

  window_operations:
    minimize_delay: 50         # Range: 0-500 ms
    restore_delay: 50          # Range: 0-500 ms
    close_delay: 100           # Range: 0-500 ms
    arrange_delay: 100         # Range: 0-1000 ms
```

## loaded_apps.yml

### Application Entry

```yaml
apps:
  - name: "Gmail"
    profile: "Work"
    app_path: "C:\\shortcuts\\Gmail-Work.lnk"
    keywords:
      - "Gmail"
      - "Google Chrome"
    priority: 1
    enabled: true
```

**Required fields:**
- `name` - Display name (string, must be unique)
- `app_path` - Path to .lnk file (string, validated by security module)
- `keywords` - Window title matching (list of strings, case-insensitive)

**Optional fields:**
- `profile` - Profile identifier (string)
- `priority` - Arrangement order (integer, must be unique, lower = first)
- `enabled` - Launch flag (boolean)

**Path requirements:**
- Only .lnk files allowed
- Absolute paths only
- No path traversal (..)
- No null bytes
- Length < 512 characters

**Priority ordering:**
- Grid: fills left-to-right, top-to-bottom
- Side-by-side: lower priority in primary pane

**Management:**
- GUI: Load Apps panel (auto-assigns priorities)
- Manual: Edit YAML, reload via F5

## load_apps.yml

### Structure

```yaml
apps:
  Zoom:
    keywords:
      - "zoom.us"
      - "zoom"
    profiles:
      - name: "Zoom"
        profile: "profile1"
        app_path: "D:\\apps\\Zoom.lnk"
        enabled: false

settings:
  apps_directory: "D:\\path\\to\\apps"
  categories:
    - "productivity"
```

**Application entry:**
- Top-level key: Application identifier
- `keywords` - Detection strings (case-insensitive)
- `profiles` - List of profile variants

**Profile fields:**
- `name` - Display name
- `profile` - Profile identifier
- `app_path` - Path to .lnk shortcut
- `enabled` - Default state (typically false)

**Keywords best practices:**
- Use specific identifiers (domain names, app names)
- Avoid generic terms ("Window", "New Tab")
- Multiple keywords improve detection

## Configuration Validation

Validation occurs on startup and configuration reload.

**Required sections:**
- `app` - name, version
- `window` - layout_mode, grid, display, timing
- `gui` - theme, window, fonts

**Validation checks:**
- YAML syntax
- Section presence
- Field types and ranges
- Unique priorities
- Path security (.lnk only, no traversal, < 512 chars)
- File existence

**Manual validation:**
```bash
python -m spectratact --validate-config
```

**Common errors:**
- Duplicate priorities: Assign unique integers
- Invalid path: Use .lnk files with absolute paths
- Missing section: Copy from docs/examples/settings.example.yml

## Live Reload

Configuration changes reload without restart:

```
File -> Reload Configuration (F5)
```

Triggers:
- Config file re-parsing
- Validation
- Auto-arrangement if priorities or layout changed
- Cache invalidation

## See Also

- [User Guide](user-guide.md) - Application operations
- [Troubleshooting](troubleshooting.md) - Configuration issues
- [API Reference](api-reference.md) - IPC interface

---

Version 0.1.0 | Beta | Python 3.8-3.13 | Node.js 18.0+ | Windows 10/11

Copyright 2025 dhaneshbb. Licensed under GPL-3.0-or-later.
