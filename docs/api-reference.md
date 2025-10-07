# API Reference

This document provides reference for Python and JavaScript APIs in SpectraTact.

## Table of Contents

- [Python API](#python-api)
  - [WindowManager](#windowmanager)
  - [ConfigValidator](#configvalidator)
  - [SecurityValidator](#securityvalidator)
  - [Path Utilities](#path-utilities)
  - [Request Handlers](#request-handlers)
- [JavaScript API](#javascript-api)
  - [IPC Handlers](#ipc-handlers)
  - [Python Bridge](#python-bridge)
- [Usage Examples](#usage-examples)
  - [Python](#python)
  - [JavaScript IPC](#javascript-ipc)
  - [Python Bridge](#python-bridge-1)
  - [Profile Management](#profile-management)
  - [Error Handling](#error-handling)
- [See Also](#see-also)

## Python API

### WindowManager

`src/spectratact/core/window_manager/manager.py`

```python
from spectratact.core.window_manager import WindowManager

manager = WindowManager(config)
```

**Methods:**

- `update_config(new_config: Dict)` - Update config, auto-arrange if changed
- `detect_displays() -> Dict` - Get display information
- `get_windows_fast() -> List[int]` - Detect windows, returns HWNDs
- `arrange_windows(display: Dict)` - Arrange using current layout
- `launch_apps_parallel() -> Dict` - Launch apps, returns `{success, launched, total, failed, valid_apps, invalid_apps}`
- `launch_specific_app(app_name: str) -> int` - Launch by name
- `minimize_all_windows() -> int` - Minimize all
- `restore_all_windows() -> int` - Restore all
- `close_all_windows() -> int` - Close all
- `close_specific_app(app_name: str) -> int` - Close by name
- `bring_window_to_front(app_name: str) -> bool` - Bring to front
- `get_active_apps() -> List[Dict]` - Returns `[{name, hwnd, title, priority, is_minimized}]`
- `refresh_window_list() -> int` - Force refresh, clear cache
- `restore_taskbar_icons() -> int` - Restore to taskbar
- `hide_all_from_taskbar() -> int` - Hide from taskbar

### ConfigValidator

`src/spectratact/config/validator.py`

```python
from spectratact.config.validator import ConfigValidator

validator = ConfigValidator()
is_valid, errors, warnings = validator.validate_config(config)
```

**Method:**

- `validate_config(config: Dict) -> Tuple[bool, List[str], List[str]]` - Returns `(is_valid, errors, warnings)`

### SecurityValidator

`src/spectratact/utils/security.py`

```python
from spectratact.utils.security import security_validator

# Validate paths
safe_path = security_validator.validate_file_path(path, {'.yml', '.lnk'}, 'context')
config_path = security_validator.validate_config_path(path)
shortcut_path = security_validator.validate_shortcut_path(path)
```

**Methods:**

- `validate_file_path(file_path: str, allowed_extensions: Set[str], context: str) -> Optional[str]` - Validate and normalize file path
- `validate_config_path(file_path: str, context: str) -> Optional[str]` - Validate config file (.yml, .yaml)
- `validate_shortcut_path(file_path: str, context: str) -> Optional[str]` - Validate shortcut file (.lnk)
- `sanitize_for_logging(text: str) -> str` - Sanitize text for safe logging
- `validate_string_input(input_str: str, max_length: int, allowed_chars: str, context: str) -> bool` - Validate string input
- `validate_numeric_input(value: Any, min_val: int, max_val: int, context: str) -> bool` - Validate numeric input

### Path Utilities

`src/spectratact/utils/paths.py`

```python
from spectratact.utils.paths import (
    get_project_root, get_config_dir, get_config_file_path,
    find_config_file, get_logs_dir, get_log_file_path
)
```

**Functions:**

- `get_project_root() -> str` - Get absolute path to project root
- `get_config_dir() -> str` - Get absolute path to config directory
- `get_config_file_path(filename: str) -> str` - Get absolute path to config file
- `find_config_file(filename: str, search_paths: List[str]) -> Optional[str]` - Find config file in multiple locations
- `get_logs_dir() -> str` - Get absolute path to logs directory
- `get_log_file_path(filename: str) -> str` - Get absolute path to log file

### Request Handlers

`src/spectratact/core/electron_bridge/handlers.py`

JSON-RPC methods for Electron frontend:

**Configuration:**
- `getConfig` - Get current config
- `reload_config` - Reload config files, returns `{success, message}`
- `updatePriorities` - Update priorities, params: `{priorities: {app: priority}}`, returns `{success, message, updated_apps, file_path}`

**Application Operations:**
- `start_apps` - Launch apps, returns `{success, count, launched, total, failed, valid_apps, invalid_apps, elapsed_time, apps_per_second}`
- `minimize_all` - Minimize all, returns `{success, count, active_apps}`
- `maximize_grid` - Arrange windows, returns `{success, count, layout, active_apps}`
- `close_all` - Close all, returns `{success, count}`
- `reopen_all` - Close and relaunch, returns `{success, count}`
- `refreshAllPages` - Send Ctrl+R, returns `{success, failed, total}`

**Specific Operations:**
- `openSpecificApp` - Launch app, params: `{name}`, returns `{success, count, app_name}`
- `closeSpecificApp` - Close app, params: `{name}`, returns `{success, count, app_name}`
- `bring_to_front` - Focus app, params: `{appName}`, returns `{success}`
- `get_active_apps` - List apps, returns `[{name, hwnd, title, priority, is_minimized}]`

**File Operations:**
- `open-settings` - Open settings.yml
- `open-apps-config` - Open loaded_apps.yml

**Profile Management:**
- `getLoadAppsConfig` - Get master profiles
- `loadSelectedProfiles` - Load profiles, params: `{appName, profiles}`
- `unloadProfile` - Remove profile, params: `{appName, profile}`
- `unloadAllProfiles` - Remove all profiles

**Health Check:**
- `ping` - Returns `{status: "ok", message: "Running"}`

## JavaScript API

### IPC Handlers

`src/desktop/main/ipc-handlers.js`

Use via `ipcRenderer.invoke(method, params)`:

**Configuration:**
- `get-config` - Get Electron config
- `getConfig` - Get Python config
- `reload-config` - Reload Electron config
- `reloadConfig` - Reload Python config
- `updateLayoutMode` - Update layout, params: `{layout_mode}`, returns `{success, layout_mode}`
- `open-config-directory` - Open config folder
- `open-settings` - Open settings.yml
- `open-apps-config` - Open loaded_apps.yml
- `open-file` - Open file, params: `filename`

**Application Operations:**
- `start-apps` - Launch apps
- `minimize-all` - Minimize all
- `maximize-grid` - Arrange windows
- `close-all` - Close all
- `reopen-all` - Relaunch all
- `get-active-apps` - List active apps
- `refreshAllPages` - Send Ctrl+R
- `bring-to-front` - Focus app, params: `appName`
- `updatePriorities` - Update priorities, params: `{app: priority}`
- `closeSpecificApp` - Close app, params: `{name}`
- `openSpecificApp` - Open app, params: `{name}`

**Window Operations:**
- `window-minimize` - Minimize main window
- `window-maximize` - Maximize/restore main window
- `window-close` - Close main window
- `toggle-always-on-top` - Toggle always on top

**Profile Management:**
- `getLoadAppsConfig` - Get profiles
- `loadSelectedProfiles` - Load profiles, params: `{appName, profiles}`
- `unloadProfile` - Remove profile, params: `{appName, profile}`
- `unloadAllProfiles` - Remove all profiles

### Python Bridge

`src/desktop/main/python-bridge.js`

```javascript
const pythonBridge = require('./main/python-bridge');
```

**Functions:**

- `startPythonBackend(getProjectDir: Function)` - Start subprocess
- `stopPythonBackend()` - Stop subprocess
- `sendCommandToPython(method: string, params: Object) -> Promise` - Send JSON-RPC command
- `getPythonProcess() -> ChildProcess | null` - Get subprocess reference
- `setAppConfig(config: Object)` - Set config for timeouts and caching

## Usage Examples

### Python

```python
from spectratact.core.window_manager import WindowManager
from spectratact.config.validator import ConfigValidator
from spectratact.utils.security import security_validator
from spectratact.utils.paths import get_config_file_path
import yaml

# Validate and load config
config_path = get_config_file_path('settings.yml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Validate configuration
validator = ConfigValidator()
is_valid, errors, warnings = validator.validate_config(config)
if not is_valid:
    for error in errors:
        print(f"ERROR: {error}")
    exit(1)

# Validate app paths
for app in config.get('apps', []):
    path = app.get('app_path')
    validated = security_validator.validate_shortcut_path(path, app['name'])
    if not validated:
        print(f"Invalid path for {app['name']}")

# Initialize and launch
manager = WindowManager(config)
result = manager.launch_apps_parallel()
print(f"Launched {result['launched']}/{result['total']} apps")
print(f"Valid: {result['valid_apps']}, Invalid: {result['invalid_apps']}")

# Detect and arrange
windows = manager.get_windows_fast()
display = manager.detect_displays()
manager.arrange_windows(display)

# Get status
apps = manager.get_active_apps()
for app in apps:
    status = "minimized" if app['is_minimized'] else "visible"
    print(f"{app['name']}: {status}")
```

### JavaScript IPC

```javascript
const { ipcRenderer } = require('electron');

// Start session
const result = await ipcRenderer.invoke('start-apps');
console.log(`Started ${result.launched} apps in ${result.elapsed_time}s`);

// Arrange windows
await ipcRenderer.invoke('maximize-grid');

// Get active apps
const apps = await ipcRenderer.invoke('get-active-apps');
apps.forEach(app => console.log(`${app.name}: ${app.title}`));

// Close session
await ipcRenderer.invoke('close-all');
```

### Python Bridge

```javascript
const pythonBridge = require('./main/python-bridge');

// Start backend
pythonBridge.startPythonBackend(() => '/path/to/project');

// Send commands
const config = await pythonBridge.sendCommandToPython('getConfig');
const result = await pythonBridge.sendCommandToPython('start_apps');
await pythonBridge.sendCommandToPython('updatePriorities', {
    priorities: { 'Gmail': 1, 'Slack': 2 }
});

// Cleanup
process.on('exit', () => pythonBridge.stopPythonBackend());
```

### Profile Management

```javascript
// Get available profiles
const profiles = await ipcRenderer.invoke('getLoadAppsConfig');

// Load profiles
await ipcRenderer.invoke('loadSelectedProfiles', {
    appName: 'Gmail',
    profiles: [
        { profile: 'Work', app_path: 'C:/shortcuts/Gmail-Work.lnk' },
        { profile: 'Personal', app_path: 'C:/shortcuts/Gmail-Personal.lnk' }
    ]
});

// Update priorities
await ipcRenderer.invoke('updatePriorities', {
    'Gmail - Work': 1,
    'Gmail - Personal': 2
});

// Unload profile
await ipcRenderer.invoke('unloadProfile', {
    appName: 'Gmail',
    profile: 'Personal'
});
```

### Error Handling

```python
# Python
try:
    result = manager.launch_apps_parallel()
    if not result['success']:
        print(f"Failed apps: {', '.join(result['failed'])}")
except Exception as e:
    print(f"Error: {str(e)}")
```

```javascript
// JavaScript
try {
    await ipcRenderer.invoke('start-apps');
} catch (error) {
    console.error('Error:', error.message);
}
```

## See Also

- [Architecture Guide](architecture.md) - System design
- [Configuration Guide](configuration.md) - Config reference
- [User Guide](user-guide.md) - Usage instructions
- [Developer Guide](developer-guide.md) - Development workflow

---

Version 0.1.0 | Beta | Python 3.8-3.13 | Node.js 18.0+ | Windows 10/11

Copyright 2025 dhaneshbb. Licensed under GPL-3.0-or-later.
