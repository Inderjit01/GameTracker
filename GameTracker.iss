; GameTracker installer script for Inno Setup

[Setup]
AppName=GameTracker
AppVersion=1.0
DefaultDirName={pf}\GameTracker
DefaultGroupName=GameTracker
UninstallDisplayIcon={app}\GameTracker.exe
OutputDir=.
OutputBaseFilename=GameTrackerInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\src\GameTracker\images\game_tracker_logo.ico

[Files]
Source: "C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\dist\GameTracker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\dist\updater.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\src\GameTracker\images\*"; DestDir: "{app}\images"; Flags: recursesubdirs
Source: "C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\src\GameTracker\styles\*"; DestDir: "{app}\styles"; Flags: recursesubdirs

[Icons]
Name: "{group}\GameTracker"; Filename: "{app}\GameTracker.exe"; IconFilename: "{app}\images\game_tracker_logo.ico"
Name: "{commondesktop}\GameTracker"; Filename: "{app}\GameTracker.exe"; IconFilename: "{app}\images\game_tracker_logo.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\GameTracker.exe"; Description: "Launch GameTracker"; Flags: nowait postinstall skipifsilent
