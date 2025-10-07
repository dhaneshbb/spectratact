# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-08

Initial beta release of SpectraTact - Desktop application management tool with intelligent window orchestration.

### Added

#### Core Architecture
- Hybrid desktop application combining Python window management with Electron GUI
- JSON-RPC communication protocol over stdin/stdout for inter-process communication
- Modular Python architecture with focused sub-modules (window_manager, electron_bridge)
- Cross-platform Electron interface supporting Windows, macOS, and Linux builds
- Entry point CLI: `python -m spectratact` with `--electron` flag (headless mode for JSON-RPC)

#### Window Management (Python)
- Window detection using Windows API (pywin32) with EnumWindows callback
- Keyword-based window matching against configured application profiles
- Priority-based window arrangement (lower number = higher priority)
- Window operations: minimize, restore, close, launch, bring-to-front
- Automatic window positioning and resizing
- Taskbar icon management (hide/restore functionality)
- Window state tracking with HWND handles and metadata

#### Layout System
- Grid layout: Configurable NxM matrix arrangement (e.g., 5x2 = 10 windows)
- Side-by-Side layout: Horizontal/vertical splits with configurable ratios
- Multi-monitor support with three distribution modes:
  - Span: Treats all displays as single canvas
  - Distribute: Evenly spreads windows across monitors
  - Primary Overflow: Fills primary display first, then overflows
- Display selection: Single (`"1"`), multiple (`"1,2"`), or auto mode
- Work area awareness: Respects taskbar and system UI boundaries
- Adaptive window sizing with configurable padding

#### Configuration System
- Three-tier YAML configuration:
  - `settings.yml`: Application behavior, layouts, performance, theme
  - `load_apps.yml`: Master library of application profiles
  - `loaded_apps.yml`: Currently active profiles with priorities
- Live configuration reload without application restart
- Configuration validation with detailed error and warning messages
- Required sections: `app`, `window`, `apps`, `gui`
- Profile structure: name, app_path, keywords, priority, enabled flag

#### Application Profile Management
- Dynamic profile loading and unloading via GUI
- Priority management with automatic conflict resolution
- Unique priority enforcement across all loaded applications
- Drag-and-drop priority reordering in profile selector
- Profile enable/disable toggle without removing from configuration
- Master profile library for quick profile switching

#### Inter-Process Communication
- ElectronBridge: JSON-RPC server with request routing to 15 handlers
- Queue-based command processing with configurable timeouts
- Async execution using ThreadPoolExecutor
- Method dispatcher for operations: start_apps, minimize_all, maximize_grid, etc.
- Callback architecture: Operations registered in main.py, invoked by bridge
- Configurable timeout values for different operation types

#### User Interface (Electron)
- BrowserWindow-based GUI with custom titlebar
- IPC handlers for 28 operations bridging renderer to Python
- Python subprocess management with automatic restart on failure
- YAML configuration loading with file watchers for live updates
- Application menu: File, Edit, Apps, View, Window, Help
- Dark/light theme switching with theme persistence
- First-run onboarding wizard for initial setup
- Application card rendering with status indicators
- Operations toolbar: Start Apps, Close All, Reopen All, Arrange, Layout Mode, Minimize, Unload All buttons

#### Performance Optimization
- Two-tier response caching:
  - Python layer: ResponseCache with 1.5s TTL for get_active_apps, getConfig
  - GUI layer: Map-based cache with 1s TTL and LRU eviction (15 entries max)
- Optimistic UI updates: Instant feedback before Python confirmation
- Background polling: Automatic state refresh every 3 seconds
- Adaptive timing for application launch based on app count
- Early exit window detection: Proceeds at 80% threshold (up to 4 attempts)
- Cache invalidation after state-changing operations
- Configurable performance settings in settings.yml

#### Security Features
- Path validation: Prevents traversal attacks, null bytes, excessive length
- File type restriction: Only .lnk files allowed for application launching
- Executable whitelist: Configurable valid_executables list
- Security validator: Centralized validation through utils/security.py
- Path sanitization for logging: Only filenames exposed, not full paths
- Length limit enforcement: 512 characters maximum for paths
- Special character detection and filtering

#### Testing Infrastructure
- Python testing with pytest:
  - 10 test files covering core functionality (conftest.py + 9 test files)
  - Test markers: unit, integration, config, windows, slow, network, filesystem, mock
  - Coverage reporting with pytest-cov
  - Fixtures for sample configurations
  - Mock support for Windows API calls
- GUI testing with Jest:
  - 5 test files for Electron components (window, python-bridge, ipc-handlers, config, menu)
  - Mock electron module for isolated testing
  - IPC handler testing
  - Coverage reporting for GUI code
- Combined test suite: `npm run test` executes both Python and GUI tests

#### Build System
- Python package (PEP 517/518):
  - Setuptools build backend
  - Entry point: `spectratact = "spectratact.main:main"`
  - Dependencies: PyYAML, psutil, pywin32
  - Development dependencies: black, flake8, pytest, pytest-cov
  - Editable install support: `pip install -e .[dev]`
- Electron Builder cross-platform packaging:
  - Windows: NSIS installer (x64, ia32) and portable executable (x64)
  - macOS: DMG and zip packages (x64, arm64)
  - Linux: AppImage, deb, rpm, tar.gz (x64)
  - Python source bundled in extraResources/spectratact/
  - Output directory: dist/SpectraTact-v{version}-{platform}/

#### Developer Tools
- Code formatting: black with 88 character line length
- Linting: flake8 with extended ignore rules (E203, W503, E501)
- Type hints: py.typed marker for PEP 561 compliance
- Configuration validators for settings and apps
- Hot reload in development mode with electron-reload
- DevTools integration for GUI debugging

#### Documentation
- User documentation:
  - Installation guide with platform-specific instructions
  - User guide covering all features and workflows
  - Configuration reference with all available options
  - Troubleshooting guide for common issues
- Developer documentation:
  - Architecture documentation explaining system design
  - API reference for all public interfaces
  - Contributing guidelines with code standards
  - Development setup instructions
- GitHub templates:
  - Bug report template with environment checklist
  - Feature request template with impact assessment
  - Pull request template with testing and quality checklists
- Example configurations in docs/examples/
- Visual assets: demo.gif, layout screenshots (grid, sidebyside, light, dark)

#### Logging
- Dual logging modes:
  - Normal mode: File + console output
  - Headless mode (--electron): File-only to avoid stdout pollution
- Log file location: logs/app.log
- Structured logging with timestamps and severity levels
- Configurable log verbosity via setup_logging()
- Separate stderr redirection to avoid JSON-RPC conflicts

#### Error Handling
- Configuration validation with detailed error messages
- Graceful fallback for missing optional configurations
- Window operation error recovery
- Python subprocess failure detection and notification
- IPC timeout handling with user feedback
- File operation safety checks with exception handling

[0.1.0]: https://github.com/dhaneshbb/spectratact/releases/tag/v0.1.0
