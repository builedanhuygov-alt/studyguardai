# PyInstaller spec for StudyGuard AI (Windows).
# Build: pyinstaller packaging/windows/studyguard.spec --noconfirm
import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(os.getcwd())

hiddenimports = (
    collect_submodules("studyguard")
    + collect_submodules("uvicorn")
    + ["fastapi", "pydantic", "webview", "pystray", "PIL.Image"]
)

datas = [
    (str(ROOT / "desktop" / "frontend"), "desktop/frontend"),
    (str(ROOT / "desktop" / "assets" / "icon.ico"), "desktop/assets"),
]

block_cipher = None

a = Analysis(
    [str(ROOT / "desktop" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["matplotlib", "tkinter"],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="StudyGuardAI",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(ROOT / "desktop" / "assets" / "icon.ico"),
    version=str(ROOT / "packaging" / "windows" / "version_info.txt"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="StudyGuardAI",
)
