#!/bin/sh
# Start the video downloader (macOS / Linux). On macOS, double-click start.command instead.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Get it from https://www.python.org/downloads/"
    exit 1
fi

if [ ! -x .venv/bin/python ]; then
    echo "First run: setting things up. This takes a minute..."
    python3 -m venv .venv && .venv/bin/python -m pip install -q -r requirements.txt || {
        echo "Setup failed. Check your internet connection and try again."
        rm -rf .venv
        exit 1
    }
fi

# Keep yt-dlp current so site changes do not break downloads.
.venv/bin/python -m pip install -q -U yt-dlp 2>/dev/null

exec .venv/bin/python app.py
