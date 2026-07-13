@echo off
chcp 65001 >nul
title TaleForge - AI Story Generator

echo ==========================================
echo      TaleForge - AI Story Generator
echo ==========================================
echo.
echo  Launching...
echo.

cd /d "%~dp0"

python start.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] TaleForge failed to start.
    echo.
)

pause
