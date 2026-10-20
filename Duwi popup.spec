# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Duwi Popup.py'],
    pathex=[],
    binaries=[],
    datas=[('Shock by @duwiexe.png', '.'), ('acquireFragment.html', '.'), ('interface.html', '.'), ('CHIMES.wav', '.')],
    hiddenimports=['webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Duwi Popup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Shock by @Duwiexe.png'],
)
