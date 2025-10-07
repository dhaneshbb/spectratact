# Installation Guide

Installation methods for SpectraTact.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Verification](#verification)
- [Configuration](#configuration)
- [Building](#building)
- [Uninstallation](#uninstallation)
- [Upgrading](#upgrading)
- [Troubleshooting](#troubleshooting)
- [See Also](#see-also)

## System Requirements

**Platform:**
- Windows 10/11 (64-bit only)
- Windows Server 2019+

**Runtime (for source installation):**
- Python 3.8+ (pyproject.toml: 3.8-3.13)
- Node.js 18.0+ (package.json engines: >=18.0.0)
- npm 7.0+

**Resources:**
- 2 GB RAM
- 200 MB disk space
- Display: 1280x720+

**Platform support:**
- Currently: Windows (pywin32-based)
- Planned: macOS (AppKit), Linux (X11/Wayland)

## Installation Methods

**From Release (Recommended):**

Download from releases page:
- NSIS installer: `SpectraTact-v0.1.0-Setup.exe` (installs to Program Files, adds to Start Menu)
- Portable: `SpectraTact-v0.1.0-Portable.exe` (runs directly, no install)

Naming from package.json build config:
```json
"nsis": {"artifactName": "${productName}-v${version}-Setup.${ext}"}
"portable": {"artifactName": "${productName}-v${version}-Portable.${ext}"}
```

**From Source (User):**

```bash
git clone https://github.com/dhaneshbb/spectratact.git
cd spectratact
pip install -r requirements.txt
npm install
npm run dev:win
```

**From Source (Developer):**

```bash
git clone https://github.com/dhaneshbb/spectratact.git
cd spectratact
pip install -e .[dev]    # Installs: psutil, pywin32, PyYAML + pytest, black, flake8, mypy
npm install
pre-commit install       # Optional
npm run dev:win
```

## Verification

**Test Python component:**
```bash
python -m spectratact
```

**Test GUI:**
```bash
npm run dev:win
```
Window should open. Check Help → About for version.

**Run tests (development):**
```bash
npm run test
```

## Configuration

On first run, SpectraTact requires three config files in `config/`:
- `settings.yml` - Application behavior
- `loaded_apps.yml` - Active profiles
- `load_apps.yml` - Profile library

Copy examples from `docs/examples/`:
```bash
cp docs/examples/settings.example.yml config/settings.yml
cp docs/examples/loaded_apps.example.yml config/loaded_apps.yml
cp docs/examples/load_apps.example.yml config/load_apps.yml
```

See [Configuration Guide](configuration.md).

## Building

```bash
npm run dist:win      # Windows: NSIS + Portable
npm run dist:mac      # macOS: DMG + ZIP (x64, arm64)
npm run dist:linux    # Linux: AppImage + deb + rpm + tar.gz
```

Output: `dist/` directory

## Uninstallation

**Installer version:**
- Settings → Apps → Installed apps → SpectraTact → Uninstall

**Portable version:**
- Delete application folder
- Remove config from `%APPDATA%\spectratact\` (optional)

**Source installation:**
```bash
pip uninstall spectratact
rm -rf node_modules dist
```

## Upgrading

**Installer:** Run new installer (preserves config)

**Source:**
```bash
git pull origin main
pip install -r requirements.txt
npm install
```

## Troubleshooting

**Python not found:**
- Install from python.org, check "Add to PATH"
- Restart terminal

**Node.js not found:**
- Install from nodejs.org (LTS version)
- Restart terminal

**pywin32 build fails:**
```bash
pip install --upgrade pywin32
```
Or install Visual C++ Build Tools

**Permission denied:**
```bash
pip install --user -r requirements.txt
```
Or run terminal as Administrator

See [Troubleshooting Guide](troubleshooting.md).

## See Also

- [User Guide](user-guide.md) - Basic operations
- [Configuration](configuration.md) - Setup
- [Developer Guide](developer-guide.md) - Development setup

---

Version 0.1.0 | Beta | Python 3.8-3.13 | Node.js 18.0+ | Windows 10/11

Copyright 2025 dhaneshbb. Licensed under GPL-3.0-or-later.
