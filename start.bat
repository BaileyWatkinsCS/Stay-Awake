@echo off
:: Start the Stay Awake application without showing a console window
:: The 'pythonw' command starts Python in windowed mode
echo Starting Stay Awake application...
start "" pythonw stay_awake.py
echo Application started! You can find it in your system tray.
timeout /t 3
