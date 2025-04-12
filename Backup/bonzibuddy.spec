# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['bonzi_buddy.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('idle/*.png', 'idle'),
        ('arrive/*.png', 'arrive'),
        ('goodbye/*.png', 'goodbye'),
        ('backflip/*.png', 'backflip'),
        ('glasses/*.png', 'glasses'),
        ('wave/*.png', 'wave'),
        ('talking/*.png', 'talking'),
        ('audio/*.wav', 'audio')
    ],
    hiddenimports=['PyQt5.QtMultimedia', 'PyQt5.sip', 'anthropic', 'yaml', 'PIL', 'requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BonziBuddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='idle/0999.png',
)

app = BUNDLE(
    exe,
    name='BonziBuddy.app',
    icon='idle/0999.png',
    bundle_identifier='com.bonzibuddy.macos',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [],
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # Makes the app appear in menu bar instead of dock
    },
)