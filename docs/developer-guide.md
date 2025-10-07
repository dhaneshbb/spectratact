# Developer Guide

Development workflows, testing, and architecture for SpectraTact contributors.

## Table of Contents

- [Setup](#setup)
- [Development](#development)
- [Code Style](#code-style)
- [Testing](#testing)
- [Architecture](#architecture)
- [Adding Features](#adding-features)
- [Debugging](#debugging)
- [Building](#building)
- [Performance](#performance)
- [Security](#security)
- [See Also](#see-also)

## Setup

Install editable Python package and dependencies:
```bash
pip install -e .[dev]
npm install
pre-commit install
```

Verify:
```bash
npm run dev:win    # Windows
npm run dev:unix   # macOS/Linux
```

## Development Commands

**Python:**
```bash
python -m spectratact              # Run Python component standalone
pytest                              # All tests
pytest test/backend/test_*.py      # Single test file
pytest -m unit                      # Unit tests only
pytest -m "not slow"               # Skip slow tests
pytest --cov=src/spectratact       # Coverage report
black src/spectratact              # Format code
flake8 src/spectratact             # Lint
mypy src/spectratact               # Type check
```

**JavaScript:**
```bash
npm run dev:win                    # Development mode (Windows)
npm run dev:unix                   # Development mode (macOS/Linux)
npm run test:frontend              # Jest tests
npm run test:frontend:watch        # Watch mode
npx eslint src/desktop             # Lint
```

**Combined:**
```bash
npm run test                       # All tests (Python + JS)
npm run pack                       # Development build (no installer)
npm run dist:win                   # Production build (Windows)
npm run dist:mac                   # Production build (macOS)
npm run dist:linux                 # Production build (Linux)
```

## Code Style

**Python (Black + Flake8 + Mypy):**
- Line length: 88
- Target: Python 3.8+
- Ignored: E203, W503, E501
- Type checking with mypy (ignores pywin32 imports)

**JavaScript (ESLint):**
- ECMAScript: 2021
- Single quotes
- Semicolons required
- Files: `src/desktop/**/*.js` (excludes `src/spectratact`)

**Pre-commit hooks (.pre-commit-config.yaml):**
- trailing-whitespace, end-of-file-fixer
- check-yaml, check-toml, check-merge-conflict
- check-added-large-files (max 2MB, excludes docs/gif|png)
- black, flake8, mypy (files: `^src/spectratact/`)
- eslint (files: `^src/desktop/.*\.js$`)

Run manually:
```bash
pre-commit run --all-files
```

## Testing

**Python (pytest):**
- 9 test files in `test/backend/`
- Markers: `unit`, `integration`, `config`, `windows`, `slow`, `network`, `filesystem`, `mock`
- Coverage target: 80% for `src/spectratact/`
- HTML report: `coverage/backend/`

**JavaScript (Jest):**
- 5 test files in `test/frontend/`
- Files: ipc-handlers, python-bridge, window, config, menu
- Coverage target: 75% for `src/desktop/main/` and `src/desktop/desktop-app.js`
- Mock electron in `test/frontend/__mocks__/electron.js`

**Debugging tests:**
```bash
pytest --pdb                       # Drop to debugger on failure
pytest -s                          # Show print statements
pytest --log-cli-level=DEBUG       # Debug logs
```

## Architecture

See [Architecture Guide](architecture.md) for complete system design.

**Communication flow:**
```
GUI (Electron) → IPC → python-bridge.js → stdin (JSON-RPC) →
Python (main.py) → handlers.py → callbacks → window_manager →
stdout (JSON response) → python-bridge.js → IPC → GUI
```

**Key files:**
- Entry: `src/spectratact/__main__.py`, `src/desktop/desktop-main.js`
- Orchestrator: `src/spectratact/main.py` (registers callbacks)
- Dispatcher: `src/spectratact/core/electron_bridge/handlers.py`
- Detection: `src/spectratact/core/window_manager/detection.py`
- Layouts: `src/spectratact/core/window_manager/layout/{grid,side_by_side}.py`
- Validation: `src/spectratact/config/validator.py`
- Security: `src/spectratact/utils/security.py`

**State:**
- Python: `app_windows` (HWND list), `window_info` (HWND → metadata dict)
- GUI: apps array, activeApps, selection
- Cache: Python 1.5s TTL, GUI 1s TTL (cleared after state-changing ops)

## Adding Features

**New window operation:**
1. Add callback in `main.py` (return dict with success/error)
2. Register in `handlers.py` (`handle_<method_name>`)
3. Add IPC handler in `ipc-handlers.js` (`ipcMain.handle`)
4. Add UI handler in `operations.js` (`ipcRenderer.invoke`)

**New layout mode:**
1. Create `src/spectratact/core/window_manager/layout/<mode>.py`
2. Implement `calculate_positions(windows, config)` returning position dicts
3. Add to `manager.py` layout_mode routing
4. Add config section to `settings.yml`
5. Update `validator.py` VALID_LAYOUT_MODES

**Platform support:**
Currently Windows-only (pywin32). For macOS/Linux:
1. Create platform abstraction in `window_manager/platforms/base.py`
2. Implement platform-specific classes (Windows/Darwin/Linux)
3. Add platform detection and factory

## Debugging

**Python:**
- Logs: `logs/app.log`
- Debug logging: Edit `setup_logging()` in `main.py`
- Breakpoints: `python -m pdb -m spectratact`
- Test subprocess: `python -m spectratact --electron`

**JavaScript:**
- DevTools: F12 or View → Toggle Developer Tools
- Main process: `electron --inspect=5858 src/desktop/desktop-main.js` (connect via `chrome://inspect`)
- Renderer: Use Console and Sources tabs

**Common issues:**
- Import errors: `pip install -e .`
- JSON-RPC failures: Add console.log in `python-bridge.js` (sent/received)
- Window detection: Test `manager.detect_windows()` directly

## Building

**Development (no installer):**
```bash
npm run pack                       # Output: dist/win-unpacked/ or dist/mac/
```

**Production:**
```bash
npm run dist:win                   # Windows: NSIS + Portable
npm run dist:mac                   # macOS: DMG + ZIP (x64, arm64)
npm run dist:linux                 # Linux: AppImage + deb + rpm + tar.gz
npm run dist:all                   # All platforms
```

**Build system (electron-builder):**
- Config: `package.json` build section
- Python bundled in `extraResources/spectratact/`
- Output: `dist/SpectraTact-v{version}-{platform}/`
- Artifacts: Setup.exe, Portable.exe, DMG, AppImage, deb, rpm

## Performance

**Python:**
- Response cache: `cache.py` (1.5s TTL)
- Threading: ThreadPoolExecutor for async operations
- Parallel app launching
- Profiling: `python -m cProfile -o profile.stats -m spectratact`

**JavaScript:**
- IPC cache: 1s TTL, max 15 entries, LRU eviction
- Optimistic UI updates (controlled by `performance.ui_updates.optimistic_updates`)
- Background polling: 3s interval
- Profiling: Chrome DevTools Performance tab

## Security

All validation in `utils/security.py` (SecurityValidator class):

**Path validation:**
- No null bytes
- No dangerous chars (|, &, ;, `, etc.)
- No path traversal (.., ~)
- Max length: 512 chars
- Only .lnk extensions
- Absolute paths only

**Executable whitelist:**
When `target_only: true`, only `valid_executables` are managed.

**Input validation:**
- YAML parsed with safe loader
- IPC params validated
- Error messages sanitized (no path disclosure)

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution workflow
- [Architecture](architecture.md) - System design
- [Configuration](configuration.md) - Config reference
- [API Reference](api-reference.md) - IPC methods

---

Version 0.1.0 | Beta | Python 3.8-3.13 | Node.js 18.0+ | Windows 10/11

Copyright 2025 dhaneshbb. Licensed under GPL-3.0-or-later.
