# Desktop Distribution

## Packaging decision (why PyInstaller + pywebview)

The entire stack — `StudyGuardService`, analytics, coach, OpenCV engine, and the
FastAPI transport — is **Python**. The desktop app must consume the *same*
service/API as the web dashboard and add nothing to the domain.

| Option | Fit for this codebase | Verdict |
| --- | --- | --- |
| **PyInstaller + pywebview** | Pure-Python bundle; reuses FastAPI + service; native window via OS WebView2; tray via `pystray`; offline | **Chosen** |
| Electron | Adds a full Node/Chromium runtime + IPC bridge to a Python sidecar | Rejected: two runtimes, ~150–250 MB, duplicate stack |
| Tauri | Tiny binary but needs Rust toolchain + a Python sidecar and IPC | Rejected: extra toolchain/complexity for no domain benefit |
| Briefcase | Good Python packager, but more opinionated config; smaller ecosystem for our WebView+tray needs | Viable; PyInstaller chosen for ubiquity + Inno Setup fit |

**Why it wins here:** no second language/toolchain, smallest maintenance surface,
reuses the exact API the dashboard uses (Desktop → Service → Domain), and stays
offline-first. WebView2 keeps the binary small vs. bundling Chromium.

## Architecture
```
desktop/main.py      orchestration: logging, crash handler, threads, tray, window
desktop/runtime.py   builds FastAPI app (REST + static SPA + /desktop/settings)
desktop/frontend/    offline SPA (index.html/app.js/styles.css) calling /api/v1
desktop/settings.py  local settings (remember last session)
desktop/paths.py     per-OS data/log/db/settings paths
```
Business logic never enters the desktop layer; it only orchestrates UI, window,
tray, notifications, and local settings.

## Requirements coverage
- Native executable, app icon, **splash** (in-SPA overlay), **About** page,
  **Settings** page, **tray** (`pystray`), **remember last session**
  (`settings.json`), **auto log folder** (`%APPDATA%/StudyGuardAI/logs`),
  **crash handling** (excepthook + native error dialog), **offline-first**,
  **installer** (Inno Setup), **portable zip**.

## Build (Windows)
```powershell
powershell -ExecutionPolicy Bypass -File packaging\windows\build_windows.ps1
```
Produces:
```
dist/StudyGuardAI/StudyGuardAI.exe      # portable build (folder)
release/StudyGuardAI-Setup-0.1.0.exe    # installer
release/StudyGuardAI-portable.zip       # portable zip (CI)
release/SHA256SUMS.txt                   # checksums
```

## macOS / Linux (documented, later)
- **macOS:** same `desktop/` code; build a `.app` with PyInstaller and sign/
  notarize; WebView backend is WKWebView (pywebview handles it).
- **Linux:** PyInstaller onedir + an AppImage; WebView backend is WebKitGTK
  (`pip install pywebview[gtk]`).
No code changes are expected — only per-OS build recipes.

## Verification status (honest)
- ✅ Generated: all desktop code, SPA, spec, installer, workflow, icon generator.
- ✅ Executed in CI-sandbox: icon generation, settings/paths/port logic, module
  compilation.
- ⚠ Requires local Windows verification: PyInstaller build, the produced `.exe`,
  the Inno Setup installer, tray/window behavior, and webcam capture.
- ❌ Not done: the `.exe` has **not** been run or tested (no Windows here).
