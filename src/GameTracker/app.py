# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 09:37:54 2025

@author: inder
"""
import sys
from PyQt5.QtWidgets import QApplication

# classes
from main_window import MainWindow
# methods
from models.db import init_db
from controllers.update_checker import check_for_updates
from background_service import run_headless
# variables
# The version of code. Used by update_checker.py to check if an update is needed.
from version import __version__

def main():
    # Create or connect to games.db
    init_db()
        
    # Creates the application object which allows events such as clicks, typing, and resizing
    app = QApplication(sys.argv)
    
    # To run the background service at boot
    IS_EXE = getattr(sys, "frozen", False)
    HEADLESS = IS_EXE and "--headless" in sys.argv
    if HEADLESS:
        run_headless(app)
    else:
        # Creates the display variables
        window = MainWindow()
        
        # Shows the mainwindow and show auto connects to app
        window.show()
        
        # Check if any updates are avalible by checking git page.
        check_for_updates(__version__, window)
    
    # app.exec_ starts the event loop
    # if the event is an exit code it will exit the program
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()