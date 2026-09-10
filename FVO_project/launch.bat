@echo off
title FVO Eagle Vulnerability Oracle
color 0A
echo.
echo  Starting FVO Eagle Vulnerability Oracle...
echo.
python main.py
if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to start. Run requirements.bat first.
    pause
)
