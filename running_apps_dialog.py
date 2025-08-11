import sys
import psutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QListWidget, QListWidgetItem, QLabel, QComboBox,
                           QLineEdit, QGroupBox, QTabWidget)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItem, QStandardItemModel

class RunningAppsDialog(QDialog):
    """Dialog to show and select from running applications"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Running Application")
        self.setMinimumSize(500, 500)
        self.selected_app = None
        self.all_processes = []  # Store all processes for filtering
        self.init_ui()
        self.populate_apps()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select an application from the list of running processes:")
        layout.addWidget(instructions)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search applications...")
        self.search_box.textChanged.connect(self.filter_apps)
        search_layout.addWidget(self.search_box)
        
        layout.addLayout(search_layout)
        
        # View type selector
        view_layout = QHBoxLayout()
        view_label = QLabel("View:")
        view_layout.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.addItem("All Processes")
        self.view_combo.addItem("Applications Only")
        self.view_combo.addItem("Background Processes")
        self.view_combo.addItem("Windows Processes")
        self.view_combo.currentIndexChanged.connect(self.filter_apps)
        view_layout.addWidget(self.view_combo)
        
        # Sort selector
        sort_label = QLabel("Sort by:")
        view_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Name (A-Z)")
        self.sort_combo.addItem("Name (Z-A)")
        self.sort_combo.currentIndexChanged.connect(self.filter_apps)
        view_layout.addWidget(self.sort_combo)
        
        layout.addLayout(view_layout)
        
        # List of running applications
        self.app_list = QListWidget()
        self.app_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.app_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.app_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_button = QPushButton("Select")
        select_button.clicked.connect(self.accept)
        button_layout.addWidget(select_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.populate_apps)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
    def populate_apps(self):
        """Collect all running processes"""
        self.all_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'username', 'cwd']):
                try:
                    # Skip processes without names
                    if not proc.info['name']:
                        continue
                    
                    # Store additional information about the process
                    proc_type = self._get_process_type(proc)
                    
                    # Store process data
                    self.all_processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'exe': proc.info['exe'] or '',
                        'type': proc_type,
                        'username': proc.info['username'] or '',
                        'cwd': proc.info['cwd'] or ''
                    })
                except:
                    # Skip processes that can't be accessed
                    continue
        except Exception as e:
            print(f"Error getting process list: {e}")
        
        # Apply initial filtering
        self.filter_apps()
    
    def _get_process_type(self, proc):
        """Determine the type of process (Application, Background, Windows)"""
        try:
            # Check if it's likely a user application
            exe = proc.info.get('exe') or ''
            name = proc.info.get('name') or ''
            username = proc.info.get('username') or ''
            
            # Windows system processes typically run as SYSTEM, NT AUTHORITY, etc.
            if 'SYSTEM' in username or 'NT AUTHORITY' in username:
                return 'Windows'
            
            # Applications typically have a GUI and are in Program Files
            if 'Program Files' in exe and not name.startswith('svc'):
                return 'Application'
                
            # Background processes
            return 'Background'
        except:
            return 'Background'
            
    def filter_apps(self):
        """Filter and display processes based on current settings"""
        self.app_list.clear()
        
        # Get filter criteria
        search_text = self.search_box.text().lower()
        view_type = self.view_combo.currentText()
        sort_type = self.sort_combo.currentText()
        
        # Filter processes
        filtered_processes = []
        for proc in self.all_processes:
            # Apply view filter
            if view_type == "Applications Only" and proc['type'] != 'Application':
                continue
            elif view_type == "Background Processes" and proc['type'] != 'Background':
                continue
            elif view_type == "Windows Processes" and proc['type'] != 'Windows':
                continue
                
            # Apply search filter
            if search_text and search_text not in proc['name'].lower():
                continue
                
            filtered_processes.append(proc)
        
        # Apply sorting
        if sort_type == "Name (A-Z)":
            filtered_processes.sort(key=lambda x: x['name'].lower())
        elif sort_type == "Name (Z-A)":
            filtered_processes.sort(key=lambda x: x['name'].lower(), reverse=True)
            
        # Remove duplicates while preserving order
        seen = set()
        unique_processes = []
        for proc in filtered_processes:
            if proc['name'] not in seen:
                unique_processes.append(proc)
                seen.add(proc['name'])
        
        # Display filtered processes
        for proc in unique_processes:
            item = QListWidgetItem(proc['name'])
            # Store the process name as user data
            item.setData(Qt.ItemDataRole.UserRole, proc['name'])
            
            # Add tooltip with more information
            tooltip = f"Name: {proc['name']}\n"
            tooltip += f"Type: {proc['type']}\n"
            if proc['exe']:
                tooltip += f"Path: {proc['exe']}\n"
            tooltip += f"PID: {proc['pid']}"
            
            item.setToolTip(tooltip)
            self.app_list.addItem(item)
            
    def accept(self):
        """Get the selected application and accept"""
        selected_items = self.app_list.selectedItems()
        if selected_items:
            self.selected_app = selected_items[0].data(Qt.ItemDataRole.UserRole)
        super().accept()
        
    def get_selected_app(self):
        """Return the selected application name"""
        return self.selected_app