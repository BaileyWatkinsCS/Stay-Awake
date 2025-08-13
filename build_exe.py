"""
Build script to create a standalone executable for Stay Awake application.
"""
import os
import subprocess
import PyInstaller.__main__
import shutil
from PIL import Image

def create_multisize_ico_from_individual_files():
    """Create a multi-size ICO file from individual size-specific ICO files."""
    print("Creating multi-size ICO from individual ICO files...")
    
    # Map of sizes to filenames
    size_files = {
        16: 'icon 16.ico',
        24: 'icon 24.ico', 
        32: 'icon 32.ico',
        48: 'icon 48.ico',
        64: 'icon 64.ico',
        96: 'icon 96.ico',
        128: 'icon 128.ico',
        256: 'icon 256.ico',
        512: 'icon.ico'  # Main icon file is 512x512
    }
    
    # Load all available sizes
    images = []
    available_sizes = []
    
    for size, filename in size_files.items():
        if os.path.exists(filename):
            try:
                img = Image.open(filename)
                # Ensure it's RGBA
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                images.append(img)
                available_sizes.append(size)
                print(f"  Loaded {filename} ({size}x{size})")
            except Exception as e:
                print(f"  Warning: Could not load {filename}: {e}")
    
    if images:
        # Save combined multi-size ICO
        multisize_path = 'windows_icon.ico'
        images[0].save(
            multisize_path,
            format='ICO',
            sizes=[(s, s) for s in available_sizes],
            append_images=images[1:]
        )
        print(f"Created multi-size ICO: {multisize_path} with sizes: {available_sizes}")
        return multisize_path
    else:
        print("No individual ICO files found")
        return None

def build_exe():
    """Build the executable using PyInstaller."""
    print("Building Stay Awake executable...")
    
    # First, create multi-size ICO from individual files
    multisize_ico = create_multisize_ico_from_individual_files()
    
    # Define PyInstaller options
    args = [
        'stay_awake.py',  # Your main script
        '--name=StayAwake',  # Name of the executable
        '--noconsole',  # No console window
        '--onefile',  # Single file executable
        '--clean',  # Clean cache before building
    ]
    
    # Use the multi-size ICO we just created, or fall back to individual files
    if multisize_ico and os.path.exists(multisize_ico):
        icon_path = os.path.abspath(multisize_ico)
        args.append(f'--icon={icon_path}')
        print(f"Using multi-size ICO: {icon_path}")
    elif os.path.exists('icon.ico'):
        icon_path = os.path.abspath('icon.ico')
        args.append(f'--icon={icon_path}')
        print(f"Using main icon.ico: {icon_path}")
    else:
        print("No icon specified")
    
    # Add data files if needed (configs, etc.)
    if os.path.exists('default_config.json'):
        args.append('--add-data=default_config.json;.')
    
    # Add icon files as data files so they're available at runtime
    if os.path.exists('windows_icon.ico'):
        args.append('--add-data=windows_icon.ico;.')
        print("Adding windows_icon.ico as data file")
    elif os.path.exists('icon.ico'):
        args.append('--add-data=icon.ico;.')
        print("Adding icon.ico as data file")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("Build completed. Executable is in the dist folder.")
    
    # Open the directory containing the executable
    dist_dir = os.path.abspath('dist')
    if os.path.exists(dist_dir):
        print(f"Executable location: {dist_dir}")
        
        # Display startup instructions
        print("\n=== Adding to Windows Startup ===")
        print("To have Stay Awake start automatically when Windows boots:")
        print("1. Press Win + R and type 'shell:startup'")
        print("2. Create a shortcut to StayAwake.exe in this folder")
        print("3. See STARTUP_GUIDE.md for more detailed instructions\n")
        
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
