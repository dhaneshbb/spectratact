@echo off
REM SpectraTact Python Setup Script
REM This script helps install Python dependencies for SpectraTact

echo SpectraTact - Python Dependency Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Found Python:
python --version
echo.

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Detected version: %PYTHON_VERSION%
echo.

REM Install dependencies
echo Installing required Python packages...
echo.

if exist "%~dp0..\requirements.txt" (
    python -m pip install --upgrade pip
    python -m pip install -r "%~dp0..\requirements.txt"

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )

    echo.
    echo SUCCESS: All Python dependencies installed
    echo.
    echo You can now run SpectraTact
) else (
    echo ERROR: requirements.txt not found
    echo Expected location: %~dp0..\requirements.txt
    pause
    exit /b 1
)

echo.
pause
