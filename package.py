# package.py
import os
import subprocess
import sys
import shutil

def package_application():
    # Install PyInstaller if not already installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean up any previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Make sure required directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("resources", exist_ok=True)
    
    # Run PyInstaller
    print("Building executable with PyInstaller...")
    pyinstaller_command = [
        "pyinstaller",
        "--name=CallSheetGenerator",
        "--windowed",  # GUI application, no console window
        "--onefile",   # Create a single executable
        "--add-data=resources:resources",  # Include resources directory
        "main.py"
    ]
    
    # Use different path separator on Windows
    if sys.platform.startswith('win'):
        pyinstaller_command[4] = "--add-data=resources;resources"
    
    subprocess.check_call(pyinstaller_command)
    
    # Create a data directory in the dist folder
    os.makedirs("dist/data", exist_ok=True)
    
    print("\nPackaging complete!")
    print(f"The executable is located in the 'dist' directory.")

if __name__ == "__main__":
    package_application()
