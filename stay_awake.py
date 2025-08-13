import sys
import os
import time
import json
import threading
from datetime import datetime, time as dt_time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, 
                           QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTimeEdit, QCheckBox, QListWidget, QListWidgetItem, QFileDialog,
                           QTabWidget, QGroupBox, QFormLayout, QRadioButton, QSlider,
                           QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTime, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QIcon, QAction
import win32api
import win32con
import psutil
import win32gui
import win32process
from weekly_schedule_dialog import WeeklyScheduleDialog

CONFIG_FILE = "stay_awake_config.json"

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


class StayAwakeWorker(QThread):
    """Worker thread to handle the stay awake functionality"""
    status_update = pyqtSignal(str)
    
    # Activity simulation types
    ACTIVITY_MOUSE_MOVEMENT = "mouse_movement"
    ACTIVITY_KEY_PRESS = "key_press"
    ACTIVITY_BOTH = "both"
    ACTIVITY_CUSTOM_KEY = "custom_key"
    
    # Default key is F15 (0x7E) - usually not present on keyboards
    DEFAULT_KEY_CODE = 0x7E
    
    def __init__(self):
        super().__init__()
        self.active = False
        self.running = True
        self.schedule_active = False
        self.app_monitoring_active = False
        self.excluded_apps = []
        self.last_action_time = time.time()
        self.weekly_schedules = None  # Will be populated with weekly schedules
        self.activity_interval = 50  # Seconds between activity simulations
        self.activity_type = self.ACTIVITY_MOUSE_MOVEMENT  # Default simulation type
        self.custom_key_code = self.DEFAULT_KEY_CODE  # Default to F15 key
        
    def toggle_active(self, state):
        self.active = state
        status = "Active" if state else "Inactive"
        self.status_update.emit(f"Status: {status}")
        
    def toggle_schedule(self, state):
        self.schedule_active = state
        # Don't emit status update from worker - let the UI handle it
        
    def toggle_app_monitoring(self, state):
        self.app_monitoring_active = state
        # Don't emit status update from worker - let the UI handle it
    
    def set_weekly_schedules(self, schedules):
        self.weekly_schedules = schedules
        # Only emit if significant (used for debugging)
        # self.status_update.emit(f"Weekly schedules updated")
        
    def set_excluded_apps(self, apps):
        self.excluded_apps = apps
        # Only emit if significant (used for debugging)
        # self.status_update.emit(f"App list updated: {len(apps)} apps")
        
    def stop(self):
        self.running = False
        
    def simulate_mouse_movement(self):
        """Simulate a tiny mouse movement"""
        try:
            x, y = win32api.GetCursorPos()
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -1, 0, 0)
            # Reset cursor to original position
            win32api.SetCursorPos((x, y))
            return True
        except Exception as e:
            self.status_update.emit(f"Error simulating mouse movement: {str(e)}")
            return False
    
    def simulate_key_press(self):
        """Simulate a harmless key press (F15 key by default which most keyboards don't have)"""
        try:
            # Use F15 key for the standard key press option (0x7E)
            key_code = self.DEFAULT_KEY_CODE
            win32api.keybd_event(key_code, 0, 0, 0)  # Key down
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            return True
        except Exception as e:
            self.status_update.emit(f"Error simulating key press: {str(e)}")
            return False
            
    def simulate_custom_key_press(self):
        """Simulate a user-defined custom key press"""
        try:
            win32api.keybd_event(self.custom_key_code, 0, 0, 0)  # Key down
            win32api.keybd_event(self.custom_key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            return True
        except Exception as e:
            self.status_update.emit(f"Error simulating custom key press: {str(e)}")
            return False
            
    def set_custom_key(self, key_code):
        """Set the custom key code to use"""
        try:
            self.custom_key_code = int(key_code, 16)  # Convert hex string to int
            self.status_update.emit(f"Custom key set to: 0x{key_code}")
            return True
        except Exception as e:
            self.status_update.emit(f"Error setting custom key: {str(e)}")
            return False
            
    def simulate_activity(self):
        """Simulate activity based on selected activity type"""
        success = False
        activity_type_str = ""
        
        try:
            if self.activity_type == self.ACTIVITY_MOUSE_MOVEMENT:
                success = self.simulate_mouse_movement()
                activity_type_str = "Mouse movement"
            elif self.activity_type == self.ACTIVITY_KEY_PRESS:
                success = self.simulate_key_press()
                activity_type_str = "Key press (F15)"
            elif self.activity_type == self.ACTIVITY_CUSTOM_KEY:
                success = self.simulate_custom_key_press()
                activity_type_str = f"Custom key press (0x{self.custom_key_code:X})"
            elif self.activity_type == self.ACTIVITY_BOTH:
                mouse_success = self.simulate_mouse_movement()
                key_success = self.simulate_key_press()
                success = mouse_success or key_success
                activity_type_str = "Mouse movement and key press"
                
            if success:
                self.last_action_time = time.time()
                self.status_update.emit(f"{activity_type_str} simulated at {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")
    
    def set_activity_interval(self, seconds):
        """Set the interval between activity simulations"""
        self.activity_interval = int(seconds)
        self.status_update.emit(f"Activity interval set to {seconds} seconds")
        
    def set_activity_type(self, activity_type):
        """Set the type of activity to simulate"""
        self.activity_type = activity_type
        type_names = {
            self.ACTIVITY_MOUSE_MOVEMENT: "Mouse movement",
            self.ACTIVITY_KEY_PRESS: "Key press (F15)",
            self.ACTIVITY_CUSTOM_KEY: f"Custom key press (0x{self.custom_key_code:X})",
            self.ACTIVITY_BOTH: "Mouse movement and key press"
        }
        self.status_update.emit(f"Activity type set to {type_names.get(activity_type, 'Unknown')}")
        
    def run(self):
        while self.running:
            # Check if we should be active
            if self.active and not self._should_be_inactive():
                # If more than the activity_interval seconds have passed since last action
                if time.time() - self.last_action_time > self.activity_interval:
                    self.simulate_activity()
            time.sleep(5)  # Check every 5 seconds
            
    def _should_be_inactive(self):
        """Check if stay awake should be inactive based on schedule or running apps"""
        # Check schedule
        if self.schedule_active and self.weekly_schedules:
            # Get current day and time
            current_day = datetime.now().strftime("%A")
            current_time = datetime.now().time()
            
            # Check if today has a schedule
            if current_day in self.weekly_schedules:
                day_schedule = self.weekly_schedules[current_day]
                
                # Check if day is enabled
                if day_schedule["enabled"]:
                    # If using global schedule
                    if day_schedule["use_global"]:
                        if self.weekly_schedules["global"]["enabled"]:
                            # Check each period in global schedule
                            for period in self.weekly_schedules["global"]["periods"]:
                                if period["enabled"]:
                                    start_time = dt_time(period["start_hour"], period["start_minute"])
                                    end_time = dt_time(period["end_hour"], period["end_minute"])
                                    if is_time_between(start_time, end_time, current_time):
                                        # We're in an active period, so should NOT be inactive
                                        return False
                            # No active periods found in global schedule
                            return True
                    else:
                        # Using custom schedule for this day
                        for period in day_schedule["periods"]:
                            if period["enabled"]:
                                start_time = dt_time(period["start_hour"], period["start_minute"])
                                end_time = dt_time(period["end_hour"], period["end_minute"])
                                if is_time_between(start_time, end_time, current_time):
                                    # We're in an active period, so should NOT be inactive
                                    return False
                        # No active periods found in day schedule
                        return True
                        
        # Check monitored apps
        if self.app_monitoring_active and self.excluded_apps:
            if is_app_running(self.excluded_apps):
                return True
                
        return False


class StayAwakeApp(QMainWindow):
    """Main window for the Stay Awake application"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stay Awake")
        self.setMinimumSize(400, 500)
        
        # Initialize activity message tracking
        self.last_activity_message = ""
        
        # Load config
        self.config = self.load_config()
        
        # Initialize UI first
        self.init_ui()
        
        # Create the worker thread
        self.worker = StayAwakeWorker()
        self.worker.status_update.connect(self.update_status)
        
        # Apply loaded settings to worker
        self.apply_config_to_worker()
        
        # Setup tray
        self.setup_tray()
        
        # Update initial status indicator based on config
        if self.config["active"]:
            self.status_indicator.setStyleSheet("color: green;")
            self.status_label.setText("Status: <b>ACTIVE</b> - your computer will not sleep")
        else:
            self.status_indicator.setStyleSheet("color: red;")
            self.status_label.setText("Status: <b>INACTIVE</b> - normal sleep settings apply")
        
        # Start worker
        self.worker.start()
        
    def load_config(self):
        """Load configuration from file"""
        # Create a WeeklyScheduleDialog instance to get default schedules
        temp_dialog = WeeklyScheduleDialog()
        default_weekly_schedules = temp_dialog.get_schedules()
        
        default_config = {
            "active": True,
            "schedule": {
                "enabled": True  # Enable scheduling by default
            },
            "weekly_schedules": default_weekly_schedules,
            "app_monitoring": {
                "enabled": False,
                "apps": []
            },
            "activity_settings": {
                "type": StayAwakeWorker.ACTIVITY_MOUSE_MOVEMENT,
                "interval": 50,
                "custom_key": "7E"  # F15 key by default (in hex)
            }
        }
        
        config = None  # Initialize config variable
        
        try:
            # First try to load user's config file
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            # If user config doesn't exist, try default config from the repository
            elif os.path.exists("default_config.json"):
                with open("default_config.json", 'r') as f:
                    config = json.load(f)
            # If running as PyInstaller executable, try to find default config in the executable
            elif hasattr(sys, '_MEIPASS'):
                default_config_path = os.path.join(sys._MEIPASS, "default_config.json")
                if os.path.exists(default_config_path):
                    with open(default_config_path, 'r') as f:
                        config = json.load(f)
            
            # If we couldn't load config from any source, use the default
            if config is None:
                config = default_config
                
            # Handle migration from old config format to new
            if "weekly_schedule" in config and "schedules" in config["weekly_schedule"]:
                # Migrate from old format
                config["weekly_schedules"] = config["weekly_schedule"]["schedules"]
                config["schedule"]["enabled"] = config["weekly_schedule"]["enabled"]
                # Remove old key
                config.pop("weekly_schedule", None)
                
            # If we're upgrading from very old config with just basic schedule
            elif "schedule" in config and "start_hour" in config["schedule"]:
                # Create a default weekly schedule with the basic schedule times
                for day in WeeklyScheduleDialog.DAYS_OF_WEEK:
                    default_weekly_schedules[day]["periods"][0].update({
                        "start_hour": config["schedule"]["start_hour"],
                        "start_minute": config["schedule"]["start_minute"],
                        "end_hour": config["schedule"]["end_hour"],
                        "end_minute": config["schedule"]["end_minute"]
                    })
                # Update the global schedule too
                default_weekly_schedules["global"]["periods"][0].update({
                    "start_hour": config["schedule"]["start_hour"],
                    "start_minute": config["schedule"]["start_minute"],
                    "end_hour": config["schedule"]["end_hour"],
                    "end_minute": config["schedule"]["end_minute"]
                })
                config["weekly_schedules"] = default_weekly_schedules
            
            # Ensure all required sections exist in older config files
            if "weekly_schedules" not in config:
                config["weekly_schedules"] = default_weekly_schedules
                
            if "activity_settings" not in config:
                config["activity_settings"] = default_config["activity_settings"]
            elif "custom_key" not in config["activity_settings"]:
                config["activity_settings"]["custom_key"] = default_config["activity_settings"]["custom_key"]
                
            return config
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return default_config
            
    def save_config(self):
        """Save configuration to file"""
        config = {
            "active": self.worker.active,
            "schedule": {
                "enabled": self.worker.schedule_active
            },
            "weekly_schedules": self.worker.weekly_schedules,
            "app_monitoring": {
                "enabled": self.worker.app_monitoring_active,
                "apps": self.get_app_list()
            },
            "activity_settings": {
                "type": self.worker.activity_type,
                "interval": self.worker.activity_interval,
                "custom_key": f"{self.worker.custom_key_code:X}"
            }
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
            
    def apply_config_to_worker(self):
        """Apply loaded config settings to the worker"""
        # Set weekly schedules
        self.worker.set_weekly_schedules(self.config["weekly_schedules"])
        
        # Set app list
        self.worker.set_excluded_apps(self.config["app_monitoring"]["apps"])
        
        # Set activity settings if they exist
        if "activity_settings" in self.config:
            self.worker.activity_type = self.config["activity_settings"]["type"]
            self.worker.activity_interval = self.config["activity_settings"]["interval"]
            
            # Set custom key if it exists
            if "custom_key" in self.config["activity_settings"]:
                self.worker.set_custom_key(self.config["activity_settings"]["custom_key"])
        
        # Update the schedule summary
        self.update_schedule_summary()
        
        # Enable features
        self.worker.toggle_schedule(self.config["schedule"]["enabled"])
        self.worker.toggle_app_monitoring(self.config["app_monitoring"]["enabled"])
        self.worker.toggle_active(self.config["active"])
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        # Combined status label with current state and last activity
        self.status_label = QLabel("Status: Inactive")
        self.status_label.setWordWrap(True)
        # Make the status label a bit taller with increased font size
        font = self.status_label.font()
        font.setPointSize(font.pointSize() + 1)
        self.status_label.setFont(font)
        status_layout.addWidget(self.status_label)
        
        # Main status and toggle button
        status_header = QHBoxLayout()
        
        # Status indicator that changes color based on active state
        self.status_indicator = QLabel("●")  # Unicode circle character
        self.status_indicator.setStyleSheet("color: red;")  # Start with red (inactive)
        status_header.addWidget(self.status_indicator)
        
        self.toggle_button = QPushButton("Turn Off" if self.config["active"] else "Turn On")
        self.toggle_button.clicked.connect(self.toggle_active)
        status_header.addWidget(self.toggle_button)
        
        # Push toggle button to the right
        status_header.addStretch()
        
        status_layout.addLayout(status_header)
        
        # Add schedule and app monitoring status labels
        features_layout = QHBoxLayout()
        
        self.schedule_status_label = QLabel(
            "Schedule: " + ("Enabled" if self.config["schedule"]["enabled"] else "Disabled")
        )
        features_layout.addWidget(self.schedule_status_label)
        
        features_layout.addSpacing(20)  # Add some spacing between labels
        
        self.app_monitoring_status_label = QLabel(
            "App Monitoring: " + ("Enabled" if self.config["app_monitoring"]["enabled"] else "Disabled")
        )
        features_layout.addWidget(self.app_monitoring_status_label)
        
        status_layout.addLayout(features_layout)
        
        # Store last activity message separately but don't display it
        self.last_activity_message = ""
        
        main_layout.addWidget(status_group)
        
        # Create tabs for features
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Application monitoring tab
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)
        
        app_header = QHBoxLayout()
        self.app_checkbox = QCheckBox("Disable when these apps are running")
        self.app_checkbox.setChecked(self.config["app_monitoring"]["enabled"])
        self.app_checkbox.toggled.connect(self.toggle_app_monitoring)
        app_header.addWidget(self.app_checkbox)
        app_layout.addLayout(app_header)
        
        self.app_list = QListWidget()
        # Add apps from config
        for app in self.config["app_monitoring"]["apps"]:
            item = QListWidgetItem(app)
            self.app_list.addItem(item)
        app_layout.addWidget(self.app_list)
        
        app_buttons = QHBoxLayout()
        add_app_button = QPushButton("Add App")
        add_app_button.clicked.connect(self.add_app)
        app_buttons.addWidget(add_app_button)
        
        remove_app_button = QPushButton("Remove App")
        remove_app_button.clicked.connect(self.remove_app)
        app_buttons.addWidget(remove_app_button)
        
        app_layout.addLayout(app_buttons)
        
        app_info = QLabel(
            "When any of the listed applications are running, "
            "the stay awake feature will be temporarily disabled."
        )
        app_info.setWordWrap(True)
        app_layout.addWidget(app_info)
        
        # Schedule tab
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout(schedule_tab)
        
        # Schedule section with enable checkbox and settings
        schedule_group = QGroupBox("Weekly Schedule")
        schedule_group_layout = QVBoxLayout(schedule_group)
        
        # Enable checkbox
        self.schedule_checkbox = QCheckBox("Enable scheduling")
        self.schedule_checkbox.setChecked(self.config["schedule"]["enabled"])
        self.schedule_checkbox.toggled.connect(self.toggle_schedule)
        schedule_group_layout.addWidget(self.schedule_checkbox)
        
        # Schedule description
        schedule_info = QLabel(
            "Configure different active hours for each day of the week.\n"
            "This allows you to create custom schedules for weekdays and weekends."
        )
        schedule_info.setWordWrap(True)
        schedule_group_layout.addWidget(schedule_info)
        
        # Button to open the weekly schedule dialog
        schedule_button = QPushButton("Configure Weekly Schedule")
        schedule_button.setMinimumHeight(36)  # Make button a bit taller
        schedule_button.clicked.connect(self.open_weekly_schedule_dialog)
        schedule_group_layout.addWidget(schedule_button)
        
        # Add the schedule group to main layout
        schedule_layout.addWidget(schedule_group)
        
        # Current schedule summary
        summary_group = QGroupBox("Current Schedule Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # Weekday summary
        weekday_label = QLabel("<b>Weekdays:</b>")
        summary_layout.addWidget(weekday_label)
        
        self.weekday_schedule_label = QLabel("Not configured")
        summary_layout.addWidget(self.weekday_schedule_label)
        
        # Weekend summary
        weekend_label = QLabel("<b>Weekends:</b>")
        summary_layout.addWidget(weekend_label)
        
        self.weekend_schedule_label = QLabel("Not configured")
        summary_layout.addWidget(self.weekend_schedule_label)
        
        # Day-specific schedules section
        self.custom_days_label = QLabel("<b>Days with custom schedules:</b>")
        summary_layout.addWidget(self.custom_days_label)
        
        self.custom_days_schedule = QLabel("None")
        self.custom_days_schedule.setWordWrap(True)
        summary_layout.addWidget(self.custom_days_schedule)
        
        # Tips for schedules
        tips_label = QLabel(
            "<b>Tips:</b> You can create multiple time slots for each day, and set "
            "different schedules for individual days of the week."
        )
        tips_label.setWordWrap(True)
        summary_layout.addWidget(tips_label)
        
        # Add the summary group to main layout
        schedule_layout.addWidget(summary_group)
        
        # Add stretch to push everything to the top
        schedule_layout.addStretch(1)
        
        # Activity Settings tab
        activity_tab = QWidget()
        activity_layout = QVBoxLayout(activity_tab)
        
        # Activity type
        activity_type_group = QGroupBox("Activity Simulation Type")
        activity_type_layout = QVBoxLayout(activity_type_group)
        
        # Radio buttons for activity types
        self.rb_mouse = QRadioButton("Mouse Movement")
        self.rb_mouse.setChecked(self.config["activity_settings"]["type"] == StayAwakeWorker.ACTIVITY_MOUSE_MOVEMENT)
        self.rb_mouse.toggled.connect(self.activity_type_changed)
        activity_type_layout.addWidget(self.rb_mouse)
        
        self.rb_keyboard = QRadioButton("Key Press (F15 key)")
        self.rb_keyboard.setChecked(self.config["activity_settings"]["type"] == StayAwakeWorker.ACTIVITY_KEY_PRESS)
        self.rb_keyboard.toggled.connect(self.activity_type_changed)
        activity_type_layout.addWidget(self.rb_keyboard)
        
        # Custom key option
        custom_key_layout = QHBoxLayout()
        self.rb_custom_key = QRadioButton("Custom Key Press:")
        self.rb_custom_key.setChecked(self.config["activity_settings"]["type"] == StayAwakeWorker.ACTIVITY_CUSTOM_KEY)
        self.rb_custom_key.toggled.connect(self.activity_type_changed)
        custom_key_layout.addWidget(self.rb_custom_key)
        
        # Input field for custom key
        self.custom_key_input = QLineEdit(self.config["activity_settings"]["custom_key"])
        self.custom_key_input.setMaxLength(4)  # Hex keys are typically 2-4 digits
        self.custom_key_input.setPlaceholderText("Hex value (e.g., 7E)")
        self.custom_key_input.textChanged.connect(self.custom_key_changed)
        self.custom_key_input.setEnabled(self.rb_custom_key.isChecked())
        custom_key_layout.addWidget(self.custom_key_input)
        
        # Help button for key codes
        custom_key_help = QPushButton("?")
        custom_key_help.setMaximumWidth(30)
        custom_key_help.clicked.connect(self.show_key_code_help)
        custom_key_layout.addWidget(custom_key_help)
        
        activity_type_layout.addLayout(custom_key_layout)
        
        self.rb_both = QRadioButton("Both Mouse and Keyboard")
        self.rb_both.setChecked(self.config["activity_settings"]["type"] == StayAwakeWorker.ACTIVITY_BOTH)
        self.rb_both.toggled.connect(self.activity_type_changed)
        activity_type_layout.addWidget(self.rb_both)
        
        activity_layout.addWidget(activity_type_group)
        
        # Activity interval
        interval_group = QGroupBox("Activity Interval")
        interval_layout = QVBoxLayout(interval_group)
        
        interval_label = QLabel("Seconds between activity simulations:")
        interval_layout.addWidget(interval_label)
        
        interval_slider_layout = QHBoxLayout()
        
        # Slider for activity interval
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(10)
        self.interval_slider.setMaximum(300)
        self.interval_slider.setValue(self.config["activity_settings"]["interval"])
        self.interval_slider.setTickInterval(30)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.valueChanged.connect(self.interval_changed)
        interval_slider_layout.addWidget(self.interval_slider)
        
        # Value label
        self.interval_value = QLabel(f"{self.config['activity_settings']['interval']} seconds")
        interval_slider_layout.addWidget(self.interval_value)
        
        interval_layout.addLayout(interval_slider_layout)
        
        interval_info = QLabel(
            "Shorter intervals keep your computer more reliably awake but may use slightly more resources. "
            "Most systems go to sleep after 60 seconds of inactivity, so values between 30-50 seconds are recommended."
        )
        interval_info.setWordWrap(True)
        interval_layout.addWidget(interval_info)
        
        activity_layout.addWidget(interval_group)
        
        # Add tabs
        tabs.addTab(schedule_tab, "Schedule")
        tabs.addTab(app_tab, "Applications")
        tabs.addTab(activity_tab, "Activity Settings")
        
    def setup_tray(self):
        """Set up the system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        # Use a standard icon since we don't have a custom one
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        toggle_action = QAction("Turn Off" if self.config["active"] else "Turn On")
        toggle_action.triggered.connect(self.toggle_active)
        tray_menu.addAction(toggle_action)
        self.tray_toggle_action = toggle_action
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def toggle_active(self):
        new_state = not self.worker.active
        self.worker.toggle_active(new_state)
        
        # Update UI
        if new_state:
            self.toggle_button.setText("Turn Off")
            self.tray_toggle_action.setText("Turn Off")
            self.status_indicator.setStyleSheet("color: green;")  # Green for active
            status_text = "Status: <b>ACTIVE</b> - your computer will not sleep"
            if self.last_activity_message:
                status_text += f"<br>{self.last_activity_message}"
        else:
            self.toggle_button.setText("Turn On")
            self.tray_toggle_action.setText("Turn On")
            self.status_indicator.setStyleSheet("color: red;")  # Red for inactive
            status_text = "Status: <b>INACTIVE</b> - normal sleep settings apply"
            
        # Update the status label with combined information
        self.status_label.setText(status_text)
            
        # Save config
        self.save_config()
            
    def toggle_schedule(self, state):
        self.worker.toggle_schedule(state)
        # Update schedule status label
        self.schedule_status_label.setText("Schedule: " + ("Enabled" if state else "Disabled"))
        
        # If disabling schedule, set all days and global schedule to disabled
        if not state and hasattr(self.worker, "weekly_schedules") and self.worker.weekly_schedules:
            # Disable the global schedule
            if "global" in self.worker.weekly_schedules:
                self.worker.weekly_schedules["global"]["enabled"] = False
            
            # Get the list of days from the WeeklyScheduleDialog class
            from weekly_schedule_dialog import WeeklyScheduleDialog
            for day in WeeklyScheduleDialog.DAYS_OF_WEEK:
                if day in self.worker.weekly_schedules:
                    self.worker.weekly_schedules[day]["enabled"] = False
                    
        # Update schedule summary to reflect the new state
        self.update_schedule_summary()
        self.save_config()
        
    def toggle_app_monitoring(self, state):
        self.worker.toggle_app_monitoring(state)
        # Update app monitoring status label
        self.app_monitoring_status_label.setText("App Monitoring: " + ("Enabled" if state else "Disabled"))
        self.save_config()
        
    # We no longer need a separate toggle_weekly_schedule method - it's consolidated with toggle_schedule
        
    def open_weekly_schedule_dialog(self):
        """Open dialog to configure weekly schedule"""
        # Ensure weekly_schedules is initialized before opening dialog
        if not hasattr(self.worker, "weekly_schedules"):
            self.worker.weekly_schedules = {}
        
        # Update the global schedule enabled state based on main schedule toggle
        # This helps synchronize the global schedule state with the main schedule toggle
        if "global" in self.worker.weekly_schedules:
            self.worker.weekly_schedules["global"]["enabled"] = self.worker.schedule_active
            
        dialog = WeeklyScheduleDialog(self, self.worker.weekly_schedules)
        if dialog.exec():
            # Get updated schedules
            self.worker.weekly_schedules = dialog.get_schedules()
            
            # Sync the main schedule toggle with global schedule state
            global_enabled = self.worker.weekly_schedules.get("global", {}).get("enabled", False)
            if self.worker.schedule_active != global_enabled:
                # Update the main schedule toggle without triggering the toggle_schedule method
                # to prevent circular references
                self.schedule_checkbox.blockSignals(True)
                self.schedule_checkbox.setChecked(global_enabled)
                self.schedule_checkbox.blockSignals(False)
                self.worker.toggle_schedule(global_enabled)
                self.schedule_status_label.setText("Schedule: " + ("Enabled" if global_enabled else "Disabled"))
            
            # Update the schedule summary display
            self.update_schedule_summary()
            self.save_config()
            # Update the schedule summary
            self.update_schedule_summary()
    
    def activity_type_changed(self):
        """Called when activity type selection is changed"""
        if self.rb_mouse.isChecked():
            self.worker.set_activity_type(StayAwakeWorker.ACTIVITY_MOUSE_MOVEMENT)
            self.custom_key_input.setEnabled(False)
        elif self.rb_keyboard.isChecked():
            self.worker.set_activity_type(StayAwakeWorker.ACTIVITY_KEY_PRESS)
            self.custom_key_input.setEnabled(False)
        elif self.rb_custom_key.isChecked():
            self.worker.set_activity_type(StayAwakeWorker.ACTIVITY_CUSTOM_KEY)
            self.custom_key_input.setEnabled(True)
            # Make sure the current custom key is applied
            self.custom_key_changed(self.custom_key_input.text())
        elif self.rb_both.isChecked():
            self.worker.set_activity_type(StayAwakeWorker.ACTIVITY_BOTH)
            self.custom_key_input.setEnabled(False)
        self.save_config()
    
    def custom_key_changed(self, text):
        """Called when the custom key input changes"""
        if not text:
            return
            
        # Try to interpret as a hex value
        try:
            # Only update if we're in custom key mode
            if self.rb_custom_key.isChecked():
                self.worker.set_custom_key(text)
                self.save_config()
        except Exception as e:
            self.status_label.setText(f"Invalid key code: {str(e)}")
            
    def show_key_code_help(self):
        """Show a dialog with information about key codes"""
        help_text = (
            "Enter a hexadecimal virtual key code (VK) to simulate.\n\n"
            "Some common keys:\n"
            "- F15: 7E (usually safe as it's not on most keyboards)\n"
            "- F16-F24: 7F-87\n"
            "- Num Lock: 90\n"
            "- Scroll Lock: 91\n"
            "- Volume Mute: AD\n"
            "- Volume Down: AE\n"
            "- Volume Up: AF\n\n"
            "Note: Be careful not to use keys that might interfere with your work."
        )
        
        QMessageBox.information(self, "Key Code Help", help_text)
    
    def interval_changed(self, value):
        """Called when activity interval slider is moved"""
        self.interval_value.setText(f"{value} seconds")
        self.worker.set_activity_interval(value)
        self.save_config()
    
    def update_schedule_summary(self):
        """Update the schedule summary display based on current schedules"""
        schedules = self.worker.weekly_schedules
        
        # Format for displaying time periods
        def format_time_periods(periods):
            times = []
            for p in periods:
                if p.get("enabled", False):
                    times.append(f"{p['start_hour']}:{p['start_minute']:02d}-{p['end_hour']}:{p['end_minute']:02d}")
            return ", ".join(times) if times else "Not configured"
        
        # Weekday summary (Monday-Friday)
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Check if all weekdays use the same schedule (global or identical custom)
        all_use_global = all(
            day in schedules and 
            schedules[day]["enabled"] and 
            schedules[day]["use_global"]
            for day in weekday_names
        )
        
        if all_use_global and schedules.get("global", {}).get("enabled", False):
            # All weekdays use global schedule
            weekday_text = format_time_periods(schedules["global"]["periods"])
            self.weekday_schedule_label.setText(f"Global schedule: {weekday_text}")
        else:
            # Check if each weekday is enabled
            enabled_weekdays = [day for day in weekday_names 
                               if day in schedules and schedules[day]["enabled"]]
            
            if not enabled_weekdays:
                self.weekday_schedule_label.setText("No weekdays enabled")
            else:
                weekday_text = ", ".join(f"{day[:3]}" for day in enabled_weekdays)
                self.weekday_schedule_label.setText(f"Enabled for: {weekday_text}")
        
        # Weekend summary (Saturday-Sunday)
        weekend_names = ["Saturday", "Sunday"]
        
        # Check if both weekend days use the same schedule
        all_use_global = all(
            day in schedules and 
            schedules[day]["enabled"] and 
            schedules[day]["use_global"]
            for day in weekend_names
        )
        
        if all_use_global and schedules.get("global", {}).get("enabled", False):
            # Both weekend days use global schedule
            weekend_text = format_time_periods(schedules["global"]["periods"])
            self.weekend_schedule_label.setText(f"Global schedule: {weekend_text}")
        else:
            # Check if each weekend day is enabled
            enabled_weekends = [day for day in weekend_names 
                              if day in schedules and schedules[day]["enabled"]]
            
            if not enabled_weekends:
                self.weekend_schedule_label.setText("No weekend days enabled")
            else:
                weekend_text = ", ".join(day for day in enabled_weekends)
                self.weekend_schedule_label.setText(f"Enabled for: {weekend_text}")
        
        # Custom day schedules
        days_with_custom = []
        for day in self.worker.weekly_schedules:
            if day != "global" and self.worker.weekly_schedules[day].get("enabled", False):
                if not self.worker.weekly_schedules[day].get("use_global", True):
                    # This day has custom schedule
                    periods = format_time_periods(self.worker.weekly_schedules[day]["periods"])
                    days_with_custom.append(f"{day}: {periods}")
        
        if days_with_custom:
            self.custom_days_label.setVisible(True)
            self.custom_days_schedule.setVisible(True)
            self.custom_days_schedule.setText("\n".join(days_with_custom))
        else:
            self.custom_days_label.setVisible(False)
            self.custom_days_schedule.setVisible(False)
        
    # We no longer need the schedule_changed method since we now use the weekly schedule dialog
        
    def add_app(self):
        """Add an application to the monitoring list"""
        # Create a dialog with options
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox
        from running_apps_dialog import RunningAppsDialog
        
        option_dialog = QDialog(self)
        option_dialog.setWindowTitle("Add Application")
        option_dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(option_dialog)
        
        # Options
        option_group = QGroupBox("Choose an option:")
        option_layout = QVBoxLayout(option_group)
        
        running_radio = QRadioButton("Select from running applications")
        running_radio.setChecked(True)
        option_layout.addWidget(running_radio)
        
        browse_radio = QRadioButton("Browse for executable file")
        option_layout.addWidget(browse_radio)
        
        layout.addWidget(option_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(option_dialog.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(option_dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Show the dialog
        if option_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        app_name = None
        
        # Handle selection based on option chosen
        if running_radio.isChecked():
            # Show running applications dialog
            running_dialog = RunningAppsDialog(self)
            if running_dialog.exec() == QDialog.DialogCode.Accepted:
                app_name = running_dialog.get_selected_app()
        else:
            # Browse for executable
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Application", 
                "", 
                "Executable Files (*.exe);;All Files (*)"
            )
            
            if file_path:
                # Extract just the filename
                app_name = os.path.basename(file_path)
        
        # Add the app to the list if we got one
        if app_name:
            # Check if it's already in the list
            existing_items = [self.app_list.item(i).text() for i in range(self.app_list.count())]
            if app_name not in existing_items:
                item = QListWidgetItem(app_name)
                self.app_list.addItem(item)
                
                # Update worker with new list
                self.worker.set_excluded_apps(self.get_app_list())
                
                # Save config
                self.save_config()
        
    def remove_app(self):
        """Remove selected application from the monitoring list"""
        selected_items = self.app_list.selectedItems()
        for item in selected_items:
            self.app_list.takeItem(self.app_list.row(item))
            
        # Update worker with new list
        self.worker.set_excluded_apps(self.get_app_list())
        
        # Save config
        self.save_config()
        
    def get_app_list(self):
        """Get list of apps from the app list widget"""
        apps = []
        for i in range(self.app_list.count()):
            apps.append(self.app_list.item(i).text())
        return apps
            
    def update_status(self, message):
        """Update the status display with activity information"""
        # Store the activity message
        if "simulated at" in message or "interval set" in message or "type set" in message:
            self.last_activity_message = message
            
            # Update the combined status label
            status_prefix = "Status: <b>ACTIVE</b> - your computer will not sleep" if self.worker.active else "Status: <b>INACTIVE</b> - normal sleep settings apply"
            self.status_label.setText(f"{status_prefix}<br>{message}")
        else:
            # For other messages, just update directly
            self.status_label.setText(message)
        
    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Stay Awake",
            "Application minimized to system tray. Click the icon to restore.",
            self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        )
        
    def close_application(self):
        """Actually close the application"""
        # Save current config before exiting
        self.save_config()
        
        # Stop the worker thread
        self.worker.stop()
        self.worker.wait()
        
        # Hide tray icon and quit
        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Prevent app from exiting when last window is closed
    app.setQuitOnLastWindowClosed(False)
    window = StayAwakeApp()
    window.show()
    sys.exit(app.exec())
