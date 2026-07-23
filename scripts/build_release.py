#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "engineering-ownership"
EXCLUDED_PARTS = {"__pycache__", ".DS_Store"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    output_dir = ROOT / "dist"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / f"engineering-ownership-v{args.version}.zip"
    timestamp = (2026, 7, 23, 0, 0, 0)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(PLUGIN.rglob("*")):
            if (
                not path.is_file()
                or any(part in EXCLUDED_PARTS for part in path.parts)
                or any(part.endswith(".egg-info") for part in path.parts)
                or path.suffix in {".pyc", ".pyo"}
            ):
                continue
            relative = path.relative_to(PLUGIN).as_posix()
            info = zipfile.ZipInfo(relative, timestamp)
            mode = 0o755 if os.access(path, os.X_OK) else 0o644
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    print(output.relative_to(ROOT))
    print(checksum.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
