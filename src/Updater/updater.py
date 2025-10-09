# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 09:03:55 2025

@author: inder
"""

import os, sys, time, subprocess, glob

def wait_for_file_close(file_path, timeout=30):
    """Wait until the specified file is no longer locked."""
    for _ in range(timeout * 2):  # 30s max
        try:
            # Try opening for exclusive read
            with open(file_path, "rb"):
                return True
        except PermissionError:
            time.sleep(0.5)
    return False


def cleanup_meipass():
    """Wait for PyInstaller's temp folder (_MEI...) to go away."""
    temp_dir = os.path.join(os.getenv("TEMP", ""), "")
    for _ in range(30):  # 15 seconds max
        mei_folders = glob.glob(os.path.join(temp_dir, "_MEI*"))
        if not mei_folders:
            return
        time.sleep(0.5)
    print("Warning: _MEI folder still exists; continuing anyway.")


def main():
    if len(sys.argv) != 3:
        print("Usage: updater.exe <path_to_app> <path_to_installer>")
        sys.exit(1)

    app_path = sys.argv[1]
    installer_path = sys.argv[2]

    print(f"Waiting for {app_path} to close...")
    wait_for_file_close(app_path)
    cleanup_meipass()

    print(f"Launching installer: {installer_path}")
    subprocess.Popen([installer_path], shell=True)
    sys.exit(0)


if __name__ == "__main__":
    main()