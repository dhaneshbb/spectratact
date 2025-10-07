# Troubleshooting Guide

Common issues and solutions for SpectraTact.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Application Launching](#application-launching)
- [Window Detection](#window-detection)
- [Window Arrangement](#window-arrangement)
- [Configuration](#configuration)
- [Performance](#performance)
- [Multi-Monitor](#multi-monitor)
- [Python Subprocess](#python-subprocess)
- [Error Messages](#error-messages)
- [Logging](#logging)
- [Getting Help](#getting-help)
- [See Also](#see-also)

## Installation Issues

**Python/Node.js not found:**
See [Installation Guide](installation.md#troubleshooting).

**Missing dependencies:**
```bash
pip install -r requirements.txt
npm install
```

**Permission denied:**
```bash
pip install --user -r requirements.txt
```
Or run terminal as Administrator.

## Application Launching

**Apps not launching:**
1. Check `enabled: true` in `loaded_apps.yml`
2. Verify `app_path` is correct .lnk file
3. Test .lnk manually in Windows Explorer
4. Check `target_only` whitelist in `settings.yml`

**Slow launching:**
```yaml
window:
  timing:
    load_wait: 6.0      # Default: 4.0
    launch_delay: 0.2   # Default: 0.1
```

## Window Detection

**Windows not detected:**
1. Check keywords match window titles (use Task Manager to verify)
2. Add multiple keywords:
```yaml
keywords:
  - "Gmail"
  - "Google Chrome"
  - "mail.google.com"
```
3. Increase `load_wait` time

**Wrong windows detected:**
Use more specific keywords:
```yaml
# Too generic
keywords: ["Chrome"]

# Specific
keywords: ["Gmail - Google Chrome", "mail.google.com"]
```

## Window Arrangement

**Windows not arranging:**
1. Verify `layout_mode: grid` or `side_by_side`
2. Check grid dimensions valid (cols/rows: 1-6)
3. Increase `timing.load_wait`
4. Reload configuration (F5)

**Wrong positions:**
Check priorities in `loaded_apps.yml`:
```yaml
apps:
  - priority: 1  # Lower = arranged first
  - priority: 2
```
Priorities must be unique.

**Windows overlap/wrong size:**
```yaml
window:
  display:
    use_work_area: true     # Respect taskbar
    preferred_display: "1"  # or "1,2" for multi-monitor
```
Grid size must accommodate window count (5x2 = 10 max).

## Configuration

**Changes not loading:**
1. Save file to `config/` directory
2. Reload: File → Reload Configuration (F5) or restart
3. Test YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('config/settings.yml'))"
```
Check for: tabs (use spaces), indentation, missing colons

**Duplicate priorities:**
Each app needs unique priority in `loaded_apps.yml`.

**Invalid path:**
Use absolute path, .lnk extension, double backslashes:
```yaml
app_path: "C:\\shortcuts\\App.lnk"
```

## Performance

**Slow startup:**
```yaml
window:
  timing:
    launch_delay: 0.2  # Default: 0.1
```

**High CPU usage:**
```yaml
performance:
  ui_updates:
    polling_interval: 5000  # Default: 3000 ms
  backend_cache:
    ttl: 3000  # Default: 1500 ms
```

**UI lag:**
```yaml
performance:
  ui_updates:
    optimistic_updates: false  # Default: true
```

## Multi-Monitor

**Windows on wrong monitor:**
```yaml
window:
  display:
    preferred_display: "1"  # or "2", "1,2", "auto"
    multi_display_mode: primary_overflow  # span, distribute, primary_overflow
```
Verify monitor numbers in Windows display settings.

**Span mode:**
```yaml
window:
  display:
    preferred_display: "1,2"
    multi_display_mode: span
```

## Python Subprocess

**Subprocess not starting:**
```bash
python -m spectratact --electron  # Test manually
pip install -r requirements.txt    # Install dependencies
```
Check `logs/app.log`.

**Timeout errors:**
```yaml
communication:
  timeouts:
    default: 12000        # Default: 8000 ms
    start_apps: 35000     # Default: 25000 ms
```

## Error Messages

**"Configuration validation failed":**
Required sections: `app`, `window`, `gui`.
Compare with `docs/examples/settings.example.yml`.

**"No applications configured":**
Load profiles via GUI or edit `loaded_apps.yml`.

**"Keywords match no windows":**
Check keywords match window titles (Task Manager).

**"Failed to arrange windows":**
Verify `layout_mode` and increase `timing.load_wait`.

## Logging

**Location:** `logs/app.log`

**View logs:**
```bash
tail -n 50 logs/app.log
grep "ERROR" logs/app.log
```

**Debug logging:**
Edit `src/spectratact/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from INFO
```

**GUI debugging:**
Press F12 or View → Toggle Developer Tools.

## Getting Help

**Before reporting:**
1. Check logs: `logs/app.log`
2. Test with example configs from `docs/examples/`
3. Verify system requirements

**Bug reports:**
Include: OS, Python/Node versions, logs, steps to reproduce.
Use template: `.github/ISSUE_TEMPLATE/bug_report.md`

## See Also

- [Configuration](configuration.md) - Settings reference
- [Installation](installation.md) - Setup
- [User Guide](user-guide.md) - Basic usage

---

Version 0.1.0 | Beta | Python 3.8-3.13 | Node.js 18.0+ | Windows 10/11

Copyright 2025 dhaneshbb. Licensed under GPL-3.0-or-later.
