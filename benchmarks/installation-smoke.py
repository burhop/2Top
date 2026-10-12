"""Check an installed studio from outside the checkout, without dev packages."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-wheel", action="store_true")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or args.port == 8000:
        parser.error("Use a separate test port")
    origin = f"http://127.0.0.1:{args.port}"
    try:
        with urlopen(origin + "/api/health", timeout=1):
            raise RuntimeError("Test port is occupied; will not reuse it")
    except OSError:
        pass
    args.output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    with tempfile.TemporaryDirectory(
        prefix="2top-first-run-", ignore_cleanup_errors=True
    ) as directory:
        started = time.monotonic()
        with (args.output / "startup.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "studio.app",
                    "--ephemeral",
                    "--port",
                    str(args.port),
                ],
                cwd=directory,
                env=env,
                stdout=log,
                stderr=log,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            try:
                for _ in range(300):
                    if process.poll() is not None:
                        raise RuntimeError(
                            f"Installed studio exited: {process.returncode}"
                        )
                    try:
                        with urlopen(origin + "/api/health", timeout=1) as response:
                            health = json.load(response)
                        break
                    except OSError:
                        time.sleep(0.1)
                else:
                    raise RuntimeError("Installed studio did not become healthy")
                startup_seconds = time.monotonic() - started
                assets = {}
                for asset in [
                    "/",
                    "/static/style.css",
                    "/static/app.js",
                    "/static/geometry.js",
                    "/static/choreography.js",
                    "/static/static-blend.js",
                    "/static/layers.js",
                    "/static/activity.js",
                    "/static/webmcp.js",
                    "/static/demo.js",
                    "/static/blend-demo.js",
                    "/static/layered-demo.js",
                    "/api/geometry?resolution=24",
                    "/api/tools",
                ]:
                    with urlopen(origin + asset, timeout=20) as response:
                        data = response.read()
                        assert data, f"Empty installed asset: {asset}"
                        assets[asset] = {"status": response.status, "bytes": len(data)}
                mcp = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "studio.mcp_client",
                        "--studio-url",
                        origin,
                        "--catalog",
                    ],
                    cwd=directory,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=True,
                )
                (args.output / "mcp-catalog.json").write_text(
                    mcp.stdout, encoding="utf-8"
                )
                catalog = json.loads(mcp.stdout)
                http_catalog = json.loads(
                    data
                )  # The final checked endpoint is /api/tools.
                assert {tool["name"] for tool in catalog["tools"]} == {
                    tool["name"] for tool in http_catalog
                }
                assert catalog["model_inference"] is False
                if args.require_wheel:
                    assert Path(
                        importlib.util.find_spec("studio").origin
                    ).is_relative_to(Path(sys.prefix))
                    assert importlib.util.find_spec("pytest") is None
                    assert importlib.util.find_spec("PySide6") is None
                scripts = Path(sys.executable).parent
                entry = scripts / (
                    "twotop-studio.exe" if os.name == "nt" else "twotop-studio"
                )
                version = subprocess.run(
                    [str(entry), "--version"],
                    cwd=directory,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()
                result = {
                    "health": health,
                    "startup_seconds": startup_seconds,
                    "python": sys.version,
                    "isolated_venv": sys.prefix != sys.base_prefix,
                    "cwd_outside_checkout": True,
                    "studio_module": importlib.util.find_spec("studio").origin,
                    "version_entrypoint": version,
                    "distribution_version": importlib.metadata.version("twotop"),
                    "assets": assets,
                    "actual_read_only_mcp_catalog": True,
                    "mcp_tool_count": len(catalog["tools"]),
                    "model_inference": False,
                    "pytest_installed": importlib.util.find_spec("pytest") is not None,
                    "pyside6_installed": importlib.util.find_spec("PySide6")
                    is not None,
                }
                (args.output / "installation.json").write_text(
                    json.dumps(result, indent=2), encoding="utf-8"
                )
                print(json.dumps(result, indent=2))
            finally:
                if os.name == "nt" and process.poll() is None:
                    # Windows venv Python redirects to a child; stop only our owned tree.
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True,
                        check=True,
                    )
                elif process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


if __name__ == "__main__":
    main()
