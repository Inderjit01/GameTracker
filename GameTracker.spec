# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

# Collect fake_useragent data files
fake_useragent_datas = collect_data_files('fake_useragent')

a = Analysis(
    ['src/GameTracker/app.py'],
    pathex=[r"C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\src\GameTracker"],
    binaries=[],
    datas=[
        ('src/GameTracker/games.db', '.'),
        ('src/GameTracker/images', 'images'),
        ('src/GameTracker/styles', 'styles'),
        ('src/GameTracker/dialogs', 'dialogs'),
        ('src/GameTracker/controllers', 'controllers'),
        ('src/GameTracker/models', 'models'),
        ('src/GameTracker/widgets', 'widgets'),
    ] + fake_useragent_datas,
    hiddenimports=[
        'controllers.api',
        'controllers.game_controller',
		'controllers.update_checker',
        'dialogs.add_game',
        'models.db',
        'widgets.game_card',
        'widgets.prices',
        'widgets.strike_label'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GameTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
	icon=r"C:\Users\inder\OneDrive\Documents\Python Projects\Game_Tracker\src\GameTracker\images\game_tracker_logo.ico",
)
