#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mhcgnomes.release_artifacts import write_release_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export lightweight runtime ontology CSVs for GitHub releases."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist-release"),
        help="Directory for release artifacts (default: dist-release)",
    )
    args = parser.parse_args()

    paths = write_release_artifacts(args.output_dir)
    for name, path in sorted(paths.items()):
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
