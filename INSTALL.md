# Stay Awake - Installation Instructions

## Running the Application

1. Navigate to the `dist` folder
2. Run `StayAwake.exe` to start the application
3. The application will appear in your system tray

## Adding to Windows Startup (Optional)

To have Stay Awake start automatically when Windows boots:

1. Press `Win + R` to open the Run dialog
2. Type `shell:startup` and press Enter
3. Create a shortcut to `StayAwake.exe` in this folder

## Troubleshooting

If the application doesn't start:

1. Make sure you have the required Visual C++ Redistributable installed
2. Try running the application as administrator
3. Check Windows Event Viewer for any error messages

## Uninstallation

1. Close the application from the system tray
2. Delete `StayAwake.exe` from your system
3. Remove any shortcuts you created

## Notes

- The executable contains all necessary dependencies and does not require Python to be installed
- Your settings will be saved in a configuration file in the same directory as the executable
