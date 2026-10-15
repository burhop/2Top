"""All published version identifiers move together for a studio update."""

import json
import tomllib
from pathlib import Path

from fastapi.testclient import TestClient

from studio import __version__
from studio.app import create_app

ROOT = Path(__file__).resolve().parents[2]


def test_package_versions_match():
    assert __version__ == "0.26.0"
    assert (
        tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
        == __version__
    )
    assert json.loads((ROOT / "package.json").read_text())["version"] == __version__
    lock = json.loads((ROOT / "package-lock.json").read_text())
    assert lock["version"] == lock["packages"][""]["version"] == __version__
    python_lock = tomllib.loads((ROOT / "uv.lock").read_text())
    project = next(p for p in python_lock["package"] if p["name"] == "twotop")
    assert project["version"] == __version__


def test_api_reports_current_version():
    with TestClient(
        create_app(enable_mcp=False), base_url="http://localhost"
    ) as client:
        assert client.get("/api/health").json()["version"] == __version__
        assert client.get("/openapi.json").json()["info"]["version"] == __version__
