# Adding Stay Awake to Windows Startup

This guide explains different methods to make the Stay Awake application start automatically when your computer boots up.

## Method 1: Windows Startup Folder (Recommended for Most Users)

This is the simplest method and works for all Windows versions.

1. First, locate your Stay Awake executable (StayAwake.exe)

2. Create a shortcut to the executable:
   - Right-click on `StayAwake.exe`
   - Select "Create shortcut"
   
3. Open the Windows Startup folder:
   - Press `Win + R` keys to open the Run dialog
   - Type `shell:startup` and press Enter
   - This opens the Startup folder for your user account

4. Move the shortcut:
   - Copy or move the shortcut you created into this Startup folder
   - The application will now start automatically when you log in

## Method 2: Task Scheduler (More Control)

This method provides more control over when and how the application starts.

1. Open Task Scheduler:
   - Search for "Task Scheduler" in the Start menu
   - Or press `Win + R`, type `taskschd.msc` and press Enter

2. Create a new task:
   - Click on "Create Basic Task" in the right panel
   - Enter "Stay Awake" as the Name
   - Optionally add a description
   - Click Next

3. Set the trigger:
   - Select "When I log on" to start when you log in
   - Click Next

4. Set the action:
   - Select "Start a program"
   - Click Next

5. Configure program details:
   - Click "Browse" and locate your `StayAwake.exe` file
   - Click Next

6. Review and finish:
   - Review your settings
   - Check "Open the Properties dialog for this task when I click Finish"
   - Click Finish

7. Additional options (in Properties dialog):
   - On the General tab, check "Run with highest privileges" if needed
   - On the Conditions tab, adjust power settings as needed
   - Click OK to save changes

## Method 3: Registry Editor (Advanced Users Only)

This method involves editing the Windows Registry. Only use this method if you're familiar with the Registry Editor.

1. Open Registry Editor:
   - Press `Win + R`
   - Type `regedit` and press Enter
   - If prompted by User Account Control, click Yes

2. Navigate to the Run key:
   - Go to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`

3. Add a new entry:
   - Right-click in the right panel
   - Select New > String Value
   - Name it "StayAwake"

4. Set the path:
   - Double-click the new "StayAwake" entry
   - Set the Value data to the full path of your StayAwake.exe file
     (e.g., `C:\Users\YourName\Programs\StayAwake\StayAwake.exe`)
   - Click OK

5. Close the Registry Editor
   - The application will now start automatically when you log in

## Troubleshooting

If Stay Awake doesn't start automatically after configuring one of these methods:

1. **Verify the executable path**: Make sure the path to StayAwake.exe is correct and has no typos.

2. **Check user permissions**: Ensure you have sufficient permissions to run the application.

3. **Check Task Scheduler**: Open Task Scheduler and check if the task is enabled and has the correct settings.

4. **Check startup items**: Press `Ctrl + Shift + Esc` to open Task Manager, go to the Startup tab, and make sure Stay Awake is enabled.

5. **Try a different method**: If one method doesn't work, try another from the list above.
