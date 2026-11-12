@echo off
rem Double-click to start the video downloader (Windows).
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed.
    echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo First run: setting things up. This takes a minute...
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
    if errorlevel 1 (
        echo Setup failed. Check your internet connection and try again.
        rmdir /s /q .venv
        pause
        exit /b 1
    )
)

rem Keep yt-dlp current so site changes do not break downloads.
".venv\Scripts\python.exe" -m pip install -q -U yt-dlp 2>nul

".venv\Scripts\python.exe" app.py
pause
