# Stay Awake

A lightweight desktop application to prevent your computer from going to sleep with customizable options.

## Features

- Prevent your computer from sleeping or activating the screensaver
- Choose between different activity simulation methods
- Set basic schedules for when the app should be active
- Configure detailed weekly schedules with different active hours for each day
- Disable the app when specific applications are running
- System tray integration for easy access
- Lightweight and minimal resource usage

## Requirements

- Python 3.6+
- PyQt6
- pywin32
- psutil
- schedule

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/stay-awake.git
cd stay-awake
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python stay_awake.py
```

## Usage

### Basic Usage

- When the application starts, it will be active by default
- Click the "Turn Off" button to temporarily disable the app
- The application minimizes to the system tray when closed
- Right-click the tray icon to access the menu

### Activity Simulation Methods

The app can keep your computer awake using different methods:
- Mouse movement: Simulates tiny mouse movements
- Key press: Simulates a key press without affecting your work
- Both: Uses both methods for maximum effectiveness

### Scheduling

Two scheduling options are available:

1. Basic Schedule:
   - Enable the basic schedule to have the app active only during specific hours
   - Set your active hours using the time selectors

2. Weekly Schedule:
   - Configure different active hours for each day of the week
   - Set up multiple active time slots per day

When outside the scheduled hours, the app will automatically disable itself.

### Application Monitoring

- Enable application monitoring to disable the app when specific applications are running
- Click "Add App" to select applications to monitor
- When any of these applications are running, the app will automatically disable

## Files in the Project

- `stay_awake.py`: Main application with all features
- `weekly_schedule_dialog.py`: Dialog for configuring weekly schedules
- `running_apps_dialog.py`: Dialog for selecting running applications
- `utils.py`: Helper functions used across the application
- `start.bat`: Batch file to start the application without a console window

## Building an Executable

You can create a standalone executable using PyInstaller:

```
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.png stay_awake.py
```

The executable will be created in the `dist` folder.

## License

MIT
