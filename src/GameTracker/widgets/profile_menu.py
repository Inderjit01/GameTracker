import sys, winreg, configparser, os
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QFrame
from PyQt5.QtCore import Qt, QPoint

# Creates/grabs the appdata path for GameTracker
APPDATA_DIR = Path(os.getenv("APPDATA")) / "GameTracker"
APPDATA_DIR.mkdir(parents=True, exist_ok=True)  # create folder if missing

# user settings stored to settings.ini
INI_FILE = APPDATA_DIR / "settings.ini"

config = configparser.ConfigParser()

def load_settings():
    if INI_FILE.exists():
        config.read(INI_FILE)
        if "General" in config:
            return {
                "background_service": config.getboolean("General", "background_service", fallback=False)
            }
    return {"background_service": False}

def save_settings(settings):
    if "General" not in config:
        config.add_section("General")
    config.set("General", "background_service", str(settings.get("background_service", False)))
    with open(INI_FILE, "w") as f:
        config.write(f)

class ProfileMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setFixedSize(200, 100)
        self.setObjectName('ProfileMenu')
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel('Settings')
        title.setObjectName('ProfileTitle')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Load settings from INI
        self.settings = load_settings()
        
        self.service_toggle = QCheckBox('Background Service')
        self.service_toggle.setChecked(self.settings.get("background_service", False))
        self.service_toggle.stateChanged.connect(self.on_toggle_service)
        layout.addWidget(self.service_toggle)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        
        status_label_str = 'OFF'
        if self.settings.get("background_service", False):
            status_label_str = 'ON'
        self.status_label = QLabel(f'Service is {status_label_str}')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    # Turns the background service on or off
    def on_toggle_service(self, state):
        self.settings["background_service"] = state == Qt.Checked
        save_settings(self.settings)
        if state == Qt.Checked:
            self.status_label.setText('Service is ON')
            self.add_to_startup()
        else:
            self.status_label.setText('Service is OFF')
            self.remove_from_startup()
     
    # displays the setting tab to the left of the settings button
    def show_near(self, button):
        button_pos = button.mapToGlobal(QPoint(0, button.height()))
        x = button_pos.x() + button.width() - self.width()
        y = button_pos.y()
        
        # Prevent popup from going outside screen bounds
        screen_geo = button.screen().geometry()
        if x + self.width() > screen_geo.right():
            x = screen_geo.right() - self.width() - 10  # Add padding
        if x < 0:
            x = 10
        
        self.move(x, y)
        self.show()
    
    # creates windows registry for auto run on boot
    def add_to_startup(self):
        exe_path = sys.executable  # dynamically detect current EXE
        command = f'"{exe_path}" --headless'
        
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as key_handle:
            winreg.SetValueEx(key_handle, "GameTracker", 0, winreg.REG_SZ, command)
    
    # removes the windows registry for auto run on boot
    def remove_from_startup(self):
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as key_handle:
            try:
                winreg.DeleteValue(key_handle, "GameTracker")
            except FileNotFoundError:
                pass
        
        
        
        
        
        
        