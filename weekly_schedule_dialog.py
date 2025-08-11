import sys
from datetime import datetime, time
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTimeEdit, QCheckBox, QTabWidget, 
                           QWidget, QGridLayout, QGroupBox, QComboBox,
                           QMessageBox)
from PyQt6.QtCore import Qt, QTime

class WeeklyScheduleDialog(QDialog):
    """Dialog to edit weekly schedules"""
    
    DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    def __init__(self, parent=None, current_schedules=None):
        super().__init__(parent)
        self.setWindowTitle("Weekly Schedule")
        self.setMinimumSize(600, 400)
        
        # Initialize schedules with defaults or current values
        self.schedules = current_schedules or self._create_default_schedules()
        
        # Initialize UI
        self.init_ui()
        
        # Load current schedules
        self.load_schedules()
        
    def _create_default_schedules(self):
        """Create default schedules for each day"""
        schedules = {}
        
        # For each day, create a default schedule
        for day in self.DAYS_OF_WEEK:
            schedules[day] = {
                "enabled": False,
                "use_global": True,
                "periods": [
                    {
                        "enabled": True,
                        "start_hour": 9,
                        "start_minute": 0,
                        "end_hour": 17,
                        "end_minute": 0
                    }
                ]
            }
            
        # Add global schedule
        schedules["global"] = {
            "enabled": False,
            "periods": [
                {
                    "enabled": True,
                    "start_hour": 9,
                    "start_minute": 0,
                    "end_hour": 17,
                    "end_minute": 0
                }
            ]
        }
        
        return schedules
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different days
        self.tab_widget = QTabWidget()
        
        # Add global settings tab
        global_tab = QWidget()
        self._setup_global_tab(global_tab)
        self.tab_widget.addTab(global_tab, "Global Schedule")
        
        # Add a tab for each day of the week
        self.day_tabs = {}
        for day in self.DAYS_OF_WEEK:
            day_tab = QWidget()
            self._setup_day_tab(day_tab, day)
            self.tab_widget.addTab(day_tab, day)
            self.day_tabs[day] = day_tab
            
        layout.addWidget(self.tab_widget)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_schedules)
        button_layout.addWidget(apply_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def _setup_global_tab(self, tab):
        """Setup the global schedule tab"""
        layout = QVBoxLayout(tab)
        
        # Global enable checkbox
        self.global_enabled = QCheckBox("Enable schedule")
        self.global_enabled.stateChanged.connect(self._on_global_enabled_changed)
        layout.addWidget(self.global_enabled)
        
        # Description
        description = QLabel(
            "The global schedule applies to all days unless a day has its own custom schedule."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Schedule periods group
        periods_group = QGroupBox("Active Periods")
        periods_layout = QVBoxLayout(periods_group)
        
        # Time slots grid: Start time - End time
        time_grid = QGridLayout()
        time_grid.addWidget(QLabel("Start Time"), 0, 0)
        time_grid.addWidget(QLabel("End Time"), 0, 1)
        
        # Create time editors for periods
        self.global_period_widgets = []
        
        # Add first period (always visible)
        period_layout = QHBoxLayout()
        
        start_time = QTimeEdit()
        start_time.setDisplayFormat("HH:mm")
        period_layout.addWidget(start_time)
        
        period_layout.addWidget(QLabel("to"))
        
        end_time = QTimeEdit()
        end_time.setDisplayFormat("HH:mm")
        period_layout.addWidget(end_time)
        
        self.global_period_widgets.append({
            "start_time": start_time,
            "end_time": end_time
        })
        
        periods_layout.addLayout(period_layout)
        
        # Add multiple periods support later if needed
        # add_period_button = QPushButton("Add Period")
        # periods_layout.addWidget(add_period_button)
        
        layout.addWidget(periods_group)
        layout.addStretch()
        
    def _setup_day_tab(self, tab, day):
        """Setup a tab for a specific day"""
        layout = QVBoxLayout(tab)
        
        # Enable checkbox
        day_enabled_layout = QHBoxLayout()
        day_enabled = QCheckBox(f"Enable custom schedule for {day}")
        day_enabled_layout.addWidget(day_enabled)
        layout.addLayout(day_enabled_layout)
        
        # Use global or custom selector
        schedule_type_layout = QHBoxLayout()
        use_global = QCheckBox("Use global schedule")
        use_global.setChecked(True)
        schedule_type_layout.addWidget(use_global)
        layout.addLayout(schedule_type_layout)
        
        # Store references to widgets
        setattr(self, f"{day.lower()}_enabled", day_enabled)
        setattr(self, f"{day.lower()}_use_global", use_global)
        
        # Connect signals
        day_enabled.stateChanged.connect(lambda state, d=day: self._on_day_enabled_changed(state, d))
        use_global.stateChanged.connect(lambda state, d=day: self._on_use_global_changed(state, d))
        
        # Custom schedule section
        custom_group = QGroupBox("Custom Schedule")
        custom_layout = QVBoxLayout(custom_group)
        
        # Period layout
        period_layout = QHBoxLayout()
        
        start_time = QTimeEdit()
        start_time.setDisplayFormat("HH:mm")
        period_layout.addWidget(start_time)
        
        period_layout.addWidget(QLabel("to"))
        
        end_time = QTimeEdit()
        end_time.setDisplayFormat("HH:mm")
        period_layout.addWidget(end_time)
        
        # Store period widgets
        setattr(self, f"{day.lower()}_start_time", start_time)
        setattr(self, f"{day.lower()}_end_time", end_time)
        
        custom_layout.addLayout(period_layout)
        layout.addWidget(custom_group)
        
        # Custom schedule group is the last widget in the layout
        setattr(self, f"{day.lower()}_custom_group", custom_group)
        
        layout.addStretch()
        
    def _on_global_enabled_changed(self, state):
        """Handle global schedule enable/disable"""
        is_enabled = bool(state)
        for period_widgets in self.global_period_widgets:
            period_widgets["start_time"].setEnabled(is_enabled)
            period_widgets["end_time"].setEnabled(is_enabled)
    
    def _on_day_enabled_changed(self, state, day):
        """Handle day schedule enable/disable"""
        is_enabled = bool(state)
        
        # Get related widgets
        use_global = getattr(self, f"{day.lower()}_use_global")
        custom_group = getattr(self, f"{day.lower()}_custom_group")
        
        # Update widgets
        use_global.setEnabled(is_enabled)
        
        # Update custom group based on both day enabled and use global
        custom_group.setEnabled(is_enabled and not use_global.isChecked())
    
    def _on_use_global_changed(self, state, day):
        """Handle use global schedule toggle"""
        use_global = bool(state)
        
        # Get custom group
        custom_group = getattr(self, f"{day.lower()}_custom_group")
        
        # Update custom group
        custom_group.setEnabled(not use_global)
    
    def load_schedules(self):
        """Load the current schedules into the UI"""
        # Load global schedule
        global_schedule = self.schedules.get("global", {})
        self.global_enabled.setChecked(global_schedule.get("enabled", False))
        
        # Load global periods
        if global_schedule.get("periods"):
            period = global_schedule["periods"][0]  # Just use the first period for now
            if period:
                start_time = QTime(period.get("start_hour", 9), period.get("start_minute", 0))
                end_time = QTime(period.get("end_hour", 17), period.get("end_minute", 0))
                self.global_period_widgets[0]["start_time"].setTime(start_time)
                self.global_period_widgets[0]["end_time"].setTime(end_time)
        
        # Load day schedules
        for day in self.DAYS_OF_WEEK:
            day_schedule = self.schedules.get(day, {})
            
            # Get widgets
            day_enabled = getattr(self, f"{day.lower()}_enabled")
            use_global = getattr(self, f"{day.lower()}_use_global")
            start_time = getattr(self, f"{day.lower()}_start_time")
            end_time = getattr(self, f"{day.lower()}_end_time")
            
            # Set values
            day_enabled.setChecked(day_schedule.get("enabled", False))
            use_global.setChecked(day_schedule.get("use_global", True))
            
            # Set time if periods exist
            if day_schedule.get("periods"):
                period = day_schedule["periods"][0]  # Just the first period
                if period:
                    start = QTime(period.get("start_hour", 9), period.get("start_minute", 0))
                    end = QTime(period.get("end_hour", 17), period.get("end_minute", 0))
                    start_time.setTime(start)
                    end_time.setTime(end)
            
            # Update enabled states
            self._on_day_enabled_changed(day_enabled.isChecked(), day)
    
    def apply_schedules(self):
        """Save the current UI state to the schedules dict"""
        # Save global schedule
        self.schedules["global"]["enabled"] = self.global_enabled.isChecked()
        
        # Save global periods
        global_start_time = self.global_period_widgets[0]["start_time"].time()
        global_end_time = self.global_period_widgets[0]["end_time"].time()
        
        self.schedules["global"]["periods"][0].update({
            "start_hour": global_start_time.hour(),
            "start_minute": global_start_time.minute(),
            "end_hour": global_end_time.hour(),
            "end_minute": global_end_time.minute()
        })
        
        # Save day schedules
        for day in self.DAYS_OF_WEEK:
            # Get widgets
            day_enabled = getattr(self, f"{day.lower()}_enabled")
            use_global = getattr(self, f"{day.lower()}_use_global")
            start_time = getattr(self, f"{day.lower()}_start_time")
            end_time = getattr(self, f"{day.lower()}_end_time")
            
            # Update schedule
            self.schedules[day]["enabled"] = day_enabled.isChecked()
            self.schedules[day]["use_global"] = use_global.isChecked()
            
            # Update period
            self.schedules[day]["periods"][0].update({
                "start_hour": start_time.time().hour(),
                "start_minute": start_time.time().minute(),
                "end_hour": end_time.time().hour(),
                "end_minute": end_time.time().minute()
            })
        
        self.accept()
        
    def get_schedules(self):
        """Return the current schedules"""
        return self.schedules
