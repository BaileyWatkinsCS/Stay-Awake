"""
Build script to create a standalone executable for Stay Awake application.
"""
import os
import subprocess
import PyInstaller.__main__
import shutil

def build_exe():
    """Build the executable using PyInstaller."""
    print("Building Stay Awake executable...")
    
    # Create an icon file from PNG if it doesn't exist
    if not os.path.exists('icon.ico') and os.path.exists('icon.png'):
        try:
            from PIL import Image
            img = Image.open('icon.png')
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save('icon.ico', sizes=icon_sizes)
            print("Created icon.ico from icon.png")
        except ImportError:
            print("Pillow not installed. Using default icon.")
        except Exception as e:
            print(f"Error creating icon.ico: {e}")
    
    # Define PyInstaller options
    args = [
        'stay_awake.py',  # Your main script
        '--name=StayAwake',  # Name of the executable
        '--noconsole',  # No console window
        '--onefile',  # Single file executable
        '--clean',  # Clean cache before building
    ]
    
    # Skip icon for now due to issues
    # if os.path.exists('icon.ico'):
    #     args.append('--icon=icon.ico')
    # elif os.path.exists('icon.png'):
    #     args.append('--icon=icon.png')
    
    # Add data files if needed (configs, etc.)
    if os.path.exists('default_config.json'):
        args.append('--add-data=default_config.json;.')
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("Build completed. Executable is in the dist folder.")
    
    # Open the directory containing the executable
    dist_dir = os.path.abspath('dist')
    if os.path.exists(dist_dir):
        print(f"Executable location: {dist_dir}")
        
        # Open explorer to the dist directory
        try:
            if os.name == 'nt':  # Windows
                os.startfile(dist_dir)
            else:
                import subprocess
                subprocess.call(['open', dist_dir])
        except:
            pass  # Ignore if can't open explorer

if __name__ == "__main__":
    # Check if Pillow is installed for icon conversion
    try:
        import PIL
    except ImportError:
        print("Pillow not installed. Attempting to install...")
        subprocess.check_call(['pip', 'install', 'Pillow'])
    
    build_exe()
