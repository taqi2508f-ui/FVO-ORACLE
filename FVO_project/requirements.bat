@echo off
title FVO Tool - Requirements Installer
color 0A

echo.
echo  ███████╗██╗   ██╗ ██████╗     ████████╗ ██████╗  ██████╗ ██╗
echo  ██╔════╝██║   ██║██╔═══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║
echo  █████╗  ██║   ██║██║   ██║       ██║   ██║   ██║██║   ██║██║
echo  ██╔══╝  ╚██╗ ██╔╝██║   ██║       ██║   ██║   ██║██║   ██║██║
echo  ██║      ╚████╔╝ ╚██████╔╝       ██║   ╚██████╔╝╚██████╔╝███████╗
echo  ╚═╝       ╚═══╝   ╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
echo.
echo  [*] FVO Vulnerability Tool - Dependency Installer
echo  [*] Checking Python installation...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.10+ from https://python.org
    echo          Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% found.
echo.

echo  [*] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo  [OK] pip upgraded.
echo.

echo  [*] Installing required packages...
echo.
pip install requests Pillow
echo.
echo  [*] Groq AI is configured inside the app.
echo      Get a key from: https://console.groq.com/keys
echo      Then click GROQ API KEY in the AI tab and paste it.

echo.
echo  ============================================================
echo   [OK] All dependencies installed successfully!
echo   [*]  Run:  python main.py
echo  ============================================================
echo.
pause
