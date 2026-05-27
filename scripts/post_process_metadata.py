import json
import os
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_DIR = Path(ROOT) / "tests" / "gallery"
SCENES_DIR = GALLERY_DIR / "scenes"
METADATA_JSON_PATH = GALLERY_DIR / "metadata.json"
METADATA_JS_PATH = GALLERY_DIR / "metadata.js"


def main():
    print("[Post-Process] Starting metadata enrichment...")

    if not METADATA_JSON_PATH.exists():
        print(
            f"[Error] metadata.json not found at {METADATA_JSON_PATH}. Wait for generator to finish."
        )
        return

    with open(METADATA_JSON_PATH, "r") as f:
        metadata = json.load(f)

    print(f"[Post-Process] Loaded {len(metadata)} records from metadata.json")

    enriched_count = 0
    for item in metadata:
        scene_id = item["id"]
        scene_file_path = SCENES_DIR / f"{scene_id}.json"

        if scene_file_path.exists():
            try:
                with open(scene_file_path, "r") as sf:
                    item["scene_data"] = json.load(sf)
                enriched_count += 1
            except Exception as e:
                print(f"[Warning] Failed to read {scene_file_path}: {e}")
                item["scene_data"] = {}
        else:
            print(f"[Warning] Scene file {scene_file_path} not found")
            item["scene_data"] = {}

    # Save enriched JSON
    with open(METADATA_JSON_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(
        f"[Post-Process] Saved enriched metadata.json (embedded {enriched_count} scene definitions)"
    )

    # Save metadata.js for CORS bypass
    with open(METADATA_JS_PATH, "w") as f:
        f.write("window.SCENE_METADATA = " + json.dumps(metadata, indent=2) + ";\n")
    print(f"[Post-Process] Saved metadata.js to {METADATA_JS_PATH}")
    print("[Post-Process] Done! The gallery is ready to view.")


if __name__ == "__main__":
    main()
