import os
import psutil
import win32gui
import win32process
from datetime import datetime, time as dt_time

def is_time_between(start_time, end_time, check_time=None):
    """Check if current time is between start and end time"""
    # If check time is not given, default to current time
    check_time = check_time or datetime.now().time()
    
    # Handle case where start is after end (spans midnight)
    if start_time <= end_time:
        return start_time <= check_time <= end_time
    else:  # Over midnight
        return check_time >= start_time or check_time <= end_time

def get_active_window_process():
    """Get the process name of the currently active window"""
    try:
        # Get handle of active window
        hwnd = win32gui.GetForegroundWindow()
        
        # Get PID from window handle
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        # Get process name from PID
        process = psutil.Process(pid)
        return process.name()
    except:
        return None

def is_app_running(app_names):
    """Check if any of the specified apps are running"""
    if not app_names:
        return False
        
    try:
        # Get all running processes
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in app_names:
                return True
        return False
    except:
        return False
