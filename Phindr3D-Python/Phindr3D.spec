# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['Phindr3D.py'],
    pathex=[],
    binaries=[],
    datas=[('phindr3d_icon.png','.'),
           ('src/GUI/windows/regex_example.png','.'),
           ('src/GUI/windows/regex_incorrect_example.png', '.')],
    hiddenimports = ['imagecodecs._imcd', 'skimage.filters.edges'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [('v', None, 'OPTION')],
    name='Phindr3D',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='phindr3d_icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
