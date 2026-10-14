"""Verify selected locked artifacts against their canonical PyPI release metadata."""

import argparse
import json
from pathlib import Path
import tomllib
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lock", type=Path, default=Path(__file__).resolve().parents[1] / "uv.lock"
    )
    parser.add_argument("--package", action="append", required=True)
    args = parser.parse_args()
    lock = tomllib.loads(args.lock.read_text(encoding="utf-8"))
    packages = {p["name"]: p for p in lock["package"]}
    for name in args.package:
        package = packages[name]
        version = package["version"]
        url = f"https://pypi.org/pypi/{quote(name, safe='')}/{quote(version, safe='')}/json"
        with urlopen(url, timeout=15) as response:
            metadata = json.load(response)
        published = {asset["filename"]: asset for asset in metadata["urls"]}
        artifacts = list(package.get("wheels", []))
        if "sdist" in package:
            artifacts.append(package["sdist"])
        if not artifacts:
            raise ValueError(f"No locked registry artifacts for {name}")
        for artifact in artifacts:
            filename = unquote(urlparse(artifact["url"]).path.rsplit("/", 1)[-1])
            reference = published.get(filename)
            if (
                reference is None
                or artifact["url"] != reference["url"]
                or artifact["hash"] != "sha256:" + reference["digests"]["sha256"]
                or artifact.get("size") != reference["size"]
            ):
                raise ValueError(
                    f"Locked artifact differs from PyPI metadata: {name} {version} {filename}"
                )
        print(f"{name} {version}: {len(artifacts)} canonical artifact records match")


if __name__ == "__main__":
    main()
