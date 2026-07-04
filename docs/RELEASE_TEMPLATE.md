# StudyGuard AI vX.Y.Z

## Highlights
- <one-line summary of the release>

## Downloads (Windows)
| Artifact | File |
| --- | --- |
| Installer | `StudyGuardAI-Setup-X.Y.Z.exe` |
| Portable | `StudyGuardAI-portable.zip` |
| Checksums | `SHA256SUMS.txt` |

Verify a download:
```powershell
Get-FileHash .\StudyGuardAI-Setup-X.Y.Z.exe -Algorithm SHA256
```

## Install & run
1. Download the installer.
2. Double-click and follow the prompts (no admin required).
3. Launch **StudyGuard AI** — grant camera access and start studying.

No Python or command line required.

## Changelog
See `CHANGELOG.md` for the full list of changes.

## Known limitations
- Windows build first; macOS/Linux recipes documented in `docs/DESKTOP.md`.
- Posture/focus and coaching are explainable heuristics (v0), not yet validated
  on real learners.
