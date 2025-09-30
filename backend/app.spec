# app.spec
# Generated manually to exclude temp, __pycache__, venv, big media files
# Build with: pyinstaller app.spec

block_cipher = None

a = Analysis(
    ['app.py'],  # entry point
    pathex=[],
    binaries=[],
    datas=[
        # Include only relevant backend code/config
        ('*.py', 'backend'),
        ('routes/*.py', 'backend'),
        ('services/*.py', 'backend'), 
        # If you have non-Python assets (like JSON, YAML), add here
        # ('backend/config/*.json', 'backend/config'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        '__pycache__', 'backend/__pycache__', 'backend/_pycache_',
        'venv', '.venv',
        'frontend',  # don’t bundle frontend build
        'temp', 'backend/temp',
        '*.avi', '*.mp4', '*.csv', '*.log', '*.txt',
        'node_modules',
        'build', 'dist',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # True → runs in terminal, False → no console
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app'
)
