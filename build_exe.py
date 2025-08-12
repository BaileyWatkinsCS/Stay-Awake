"""
Build script to create a standalone executable for Stay Awake application.
"""
import os
import subprocess
import PyInstaller.__main__
import shutil
from PIL import Image

def build_exe():
    """Build the executable using PyInstaller."""
    print("Building Stay Awake executable...")
    
    # Create a properly formatted Windows icon file
    windows_icon_path = 'windows_icon.ico'
    if os.path.exists('icon.png') and (not os.path.exists(windows_icon_path) or os.path.getsize(windows_icon_path) < 1000):
        try:
            # Open the image and ensure it's RGBA (transparent background)
            img = Image.open('icon.png')
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Standard Windows icon sizes
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Create a transparent background for each size
            resized_imgs = []
            for size in sizes:
                # Create a new transparent image
                new_img = Image.new('RGBA', size, (0, 0, 0, 0))
                
                # Resize the original image proportionally to fit within the size
                ratio = min(size[0] / img.width, size[1] / img.height)
                resized_width = int(img.width * ratio)
                resized_height = int(img.height * ratio)
                resized = img.resize((resized_width, resized_height), Image.LANCZOS)
                
                # Calculate position to center the image
                pos_x = (size[0] - resized_width) // 2
                pos_y = (size[1] - resized_height) // 2
                
                # Paste the resized image onto the transparent background
                new_img.paste(resized, (pos_x, pos_y), resized)
                resized_imgs.append(new_img)
            
            # Save as ICO
            resized_imgs[0].save(windows_icon_path, format='ICO', 
                               sizes=[(img.size[0], img.size[1]) for img in resized_imgs],
                               append_images=resized_imgs[1:])
            
            print(f"Created standard Windows icon at {windows_icon_path}")
        except ImportError:
            print("Pillow not installed. Using default icon.")
        except Exception as e:
            print(f"Error creating icon: {e}")
    
    # Define PyInstaller options
    args = [
        'stay_awake.py',  # Your main script
        '--name=StayAwake',  # Name of the executable
        '--noconsole',  # No console window
        '--onefile',  # Single file executable
        '--clean',  # Clean cache before building
    ]
    
    # Use the standard Windows icon that we created
    if os.path.exists('windows_icon.ico'):
        icon_path = os.path.abspath('windows_icon.ico')
        args.append(f'--icon={icon_path}')
        print(f"Using standard Windows icon: {icon_path}")
    elif os.path.exists('app_icon.ico'):
        icon_path = os.path.abspath('app_icon.ico')
        args.append(f'--icon={icon_path}')
        print(f"Using app_icon.ico: {icon_path}")
    elif os.path.exists('icon.ico'):
        icon_path = os.path.abspath('icon.ico')
        args.append(f'--icon={icon_path}')
        print(f"Using icon.ico: {icon_path}")
    elif os.path.exists('icon.png'):
        icon_path = os.path.abspath('icon.png')
        args.append(f'--icon={icon_path}')
        print(f"Using icon.png directly: {icon_path}")
    else:
        print("No icon specified")
    
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
