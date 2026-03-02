#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def check_environment():
    """Checking if the program is running inside the correct virtual environment"""
    venv_path = os.environ.get('VIRTUAL_ENV')
    if not venv_path:
        raise Exception("ERROR: Not running in a virtual environment")
    
    env_name = os.path.basename(venv_path)
    if env_name != 'kindraer':
        raise Exception(f"ERROR: Running in wrong environment '{env_name}'. Expected 'kindraer'")
    
    print(f"OK - Running in correct environment: {venv_path}")

def install_libraries():
    """Installing libraries using Requirements.txt"""
    # Creating a temporary requirements file with the two packages
    with open('temp_requirements.txt', 'w') as f:
        f.write("beautifulsoup4\npytest\ntermgraph\n")
    
    # Install using the requirements file
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'temp_requirements.txt'], 
                      check=True)
        print("OK - Successfully installed BeautifulSoup and PyTest")
    finally:
        # Clean up temporary file
        if os.path.exists('temp_requirements.txt'):
            os.remove('temp_requirements.txt')

def display_and_save_requirements():
    """Displaying installed libraries and save to requirements.txt"""
    # Get installed packages
    result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                          capture_output=True, text=True, check=True)
    
    packages = result.stdout.strip().split('\n')
    
    # Display packages
    print("\nInstalled libraries:")
    for package in sorted(packages):
        print(package)
    
    # Save to requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write(result.stdout)
    
    print(f"\nOK- Saved {len(packages)} packages to requirements.txt")

def create_environment_archive():
    """Creating an archive of the virtual environment"""
    env_path = os.environ.get('VIRTUAL_ENV')
    if not env_path:
        return
    
    archive_name = 'kindraer_env'
    
    # Create tar archive (compressed)
    shutil.make_archive(archive_name, 'gztar', os.path.dirname(env_path), 'kindraer')
    print(f"OK - Created environment archive: {archive_name}.tar.gz")


if __name__ == "__main__":
    try:
        print("Starting library installation process...")
        
        check_environment()
        
        install_libraries()
        
        display_and_save_requirements()
        
        create_environment_archive()
        
        print("OK - All tasks completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)