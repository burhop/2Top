"""CLI tool for inspecting and regenerating golden digests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from tests.golden.loader import DIGEST_DIR, load_digest
from tests.helpers.builders import build_axis_aligned_rectangle, composite_perimeter


def _composite_square_digest() -> Dict[str, Dict[str, float]]:
    rect = build_axis_aligned_rectangle(0.0, 0.0, 1.0, 1.0)
    bbox = rect.bounding_box()
    area = (bbox[1] - bbox[0]) * (bbox[3] - bbox[2])
    perimeter = composite_perimeter(rect)
    return {
        "unit_square": {
            "perimeter": perimeter,
            "area": area,
            "bounding_box": list(map(float, bbox)),
        }
    }


GENERATORS = {
    "composite_square": _composite_square_digest,
}


def regenerate_digest(name: str) -> Dict[str, Dict[str, float]]:
    try:
        generator = GENERATORS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown digest name: {name}") from exc
    return generator()


def main() -> None:
    parser = argparse.ArgumentParser(description="Golden digest utility")
    parser.add_argument("name", help="Digest name (e.g., composite_square)")
    parser.add_argument("--write", action="store_true", help="Persist regenerated digest to file")
    parser.add_argument("--show", action="store_true", help="Print digest contents")
    args = parser.parse_args()

    digest = regenerate_digest(args.name)
    if args.write:
        DIGEST_DIR.mkdir(parents=True, exist_ok=True)
        path = DIGEST_DIR / f"{args.name}.json"
        path.write_text(json.dumps(digest, indent=2))
        print(f"Wrote digest to {path}")

    if args.show or not args.write:
        print(json.dumps(digest, indent=2))


if __name__ == "__main__":
    main()
