import requests, sys, os, tempfile, subprocess, time
from PyQt5.QtWidgets import QMessageBox

VERSION_URL = 'https://raw.githubusercontent.com/Inderjit01/GameTracker/refs/heads/main/version.txt'
INSTALLER_URL = 'https://github.com/Inderjit01/GameTracker/releases/latest/download/GameTrackerInstaller.exe'

def check_for_updates(current_version, parent=None):
    # Deletes old installer if it exists
    cleanup_old_installer()
    
    try:
        # Grabs the version text file on Git
        response = requests.get(VERSION_URL, timeout=5)
        response.raise_for_status()
        if response.status_code != 200:
            print('Failed checking for update: Invalid reponse from server.')
            return
        
        latest_version = float(response.text.strip())
        
        print(f'GIT VERSION: {latest_version}')
        print(f'CURRENT VERSION: {current_version}')
        print()
        
        # Run the update window prompt if the current version is outdated
        if latest_version > current_version:
            msg = QMessageBox(parent)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle('Update Available')
            msg.setText(f'A new version ({latest_version}) is available!')
            msg.setInformativeText('Do you want to download and install the update now?')
            yes_button = msg.addButton('Update', QMessageBox.AcceptRole)
            msg.addButton('Later', QMessageBox.RejectRole)
            msg.exec_()
            
            if msg.clickedButton() == yes_button:
                download_and_run_installer()
                sys.exit()
        
    except Exception as e:
        print(f'Updated check failed: {e}')

# Removes old installer
def cleanup_old_installer():
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, 'GameTrackerInstaller.exe')
    if os.path.exists(installer_path):
        try:
            os.remove(installer_path)
            print(f"Deleted leftover installer: {installer_path}")
        except Exception as e:
            print(f"Could not delete installer: {e}")

# If users selects to update then download the installer from Git and run it.
def download_and_run_installer():
    try:
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, 'GameTrackerInstaller.exe')

        # Download latest installer
        print(f"Downloading installer from {INSTALLER_URL}")
        r = requests.get(INSTALLER_URL, stream=True)
        r.raise_for_status()
        with open(installer_path, 'wb') as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

        # Path to the installed updater.exe
        app_dir = os.path.dirname(sys.argv[0])
        updater_path = os.path.join(app_dir, "updater.exe")

        print(f"Launching updater: {updater_path}")
        # Runs the updater.exe
        subprocess.Popen([updater_path, sys.argv[0], installer_path], shell=True)

        # Give updater a moment to start
        time.sleep(0.5)
        sys.exit(0)

    except Exception as e:
        print(f"Failed to run update: {e}")