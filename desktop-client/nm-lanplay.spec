# -*- mode: python ; coding: utf-8 -*-
# Build: pip install pyinstaller && pyinstaller nm-lanplay.spec

a = Analysis(
    ['nm-lanplay.py'],
    binaries=[('bin/lan-play.exe', 'bin')],
    datas=[('assets/', 'assets/')],
    hiddenimports=[],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='NM-LanPlay', debug=False, console=False,
    icon='assets/logo.ico')
