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

### From Source
1. Clone the repository:
```
git clone https://github.com/BaileyWatkinsCS/Stay-Awake.git
cd Stay-Awake
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python stay_awake.py
```

### From Executable

1. Download the latest release from the [Releases page](https://github.com/BaileyWatkinsCS/Stay-Awake/releases)
2. Extract the zip file
3. Run `StayAwake.exe`

### Adding to Windows Startup

To have Stay Awake start automatically when Windows starts:

#### Method 1: Startup Folder
1. Press `Win + R` to open the Run dialog
2. Type `shell:startup` and press Enter
3. Copy the `StayAwake.exe` shortcut or create a new shortcut to the executable in this folder

#### Method 2: Task Scheduler
1. Search for "Task Scheduler" in the Start menu and open it
2. Click "Create Basic Task" in the right panel
3. Name it "Stay Awake" and click Next
4. Select "When I log on" as the trigger and click Next
5. Select "Start a program" as the action and click Next
6. Browse to the location of your `StayAwake.exe` file
7. Click Next and then Finish

#### Method 3: Registry (Advanced)
1. Press `Win + R`, type `regedit` and press Enter
2. Navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Right-click in the right panel and select New > String Value
4. Name it "StayAwake"
5. Double-click it and set the value to the full path of your `StayAwake.exe` file (e.g., `C:\Path\To\StayAwake.exe`)

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

## Configuration

The application uses JSON configuration files to save user preferences:

- `stay_awake_config.json`: Created automatically when you run the app and save settings
- `default_config.json`: Default configuration provided in the repository

The user-specific configuration file (`stay_awake_config.json`) is included in `.gitignore` to avoid committing personal settings to the repository.

## Building an Executable

You can create a standalone executable using the provided build script:

```
python build_exe.py
```

Alternatively, you can use PyInstaller directly:

```
pip install pyinstaller
pyinstaller --onefile --noconsole --name=StayAwake stay_awake.py
```

The executable will be created in the `dist` folder. The build artifacts are included in `.gitignore` to keep the repository clean.

## License

MIT
