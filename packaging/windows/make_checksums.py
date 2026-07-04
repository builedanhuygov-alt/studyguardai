"""Generate SHA-256 checksums for release artifacts.

Writes release/SHA256SUMS.txt covering the installer and any portable zip found
in the release/ and dist/ folders. Standard library only.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "release"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    candidates = sorted(
        [p for p in RELEASE.glob("*") if p.suffix.lower() in {".exe", ".zip"}]
    )
    lines = [f"{_sha256(path)}  {path.name}" for path in candidates]
    output = RELEASE / "SHA256SUMS.txt"
    output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"wrote {output} ({len(lines)} artifact(s))")


if __name__ == "__main__":
    main()
