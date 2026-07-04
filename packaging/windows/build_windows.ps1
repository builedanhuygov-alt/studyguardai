# Build the StudyGuard AI Windows executable + installer.
# Prereqs: Windows, Python 3.12, Inno Setup 6 (iscc on PATH).
# Usage:  powershell -ExecutionPolicy Bypass -File packaging\windows\build_windows.ps1
$ErrorActionPreference = "Stop"

Write-Host "==> Creating virtual environment"
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Write-Host "==> Installing project + build deps"
python -m pip install --upgrade pip
pip install -e ".[api,desktop]"
pip install pyinstaller>=6.0

Write-Host "==> Generating icon"
python packaging\windows\make_icon.py

Write-Host "==> Building executable (PyInstaller)"
pyinstaller packaging\windows\studyguard.spec --noconfirm

Write-Host "==> Building installer (Inno Setup)"
if (Get-Command iscc -ErrorAction SilentlyContinue) {
    iscc packaging\windows\installer.iss
} else {
    Write-Warning "iscc not found; skipping installer. Install Inno Setup 6."
}

Write-Host "==> Generating checksums"
python packaging\windows\make_checksums.py

Write-Host "==> Done. Artifacts in dist\ and release\"
