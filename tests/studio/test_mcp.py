"""Protocol integration tests use the official MCP 2.x client, not RPC mocks."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from contextlib import asynccontextmanager

import httpx
import httpx2
import pytest
import uvicorn
from mcp import Client
from mcp.client.stdio import StdioServerParameters
from mcp.client.streamable_http import streamable_http_client

from studio.mcp_server import RemoteStudioBackend, create_mcp_server
from studio.service import SceneService

ROOT = Path(__file__).resolve().parents[2]


@asynccontextmanager
async def http_mcp_client(url):
    # Loopback integration must not inherit a machine's outbound SOCKS proxy.
    async with httpx2.AsyncClient(trust_env=False) as http:
        transport = streamable_http_client(url, http_client=http)
        async with Client(transport) as client:
            yield client


def payload(result):
    assert result.structured_content is not None
    assert json.loads(result.content[0].text) == result.structured_content
    return result.structured_content


@pytest.mark.asyncio
async def test_official_client_discovers_exact_service_schemas_and_protocol():
    service = SceneService()
    async with Client(create_mcp_server(service)) as client:
        assert client.protocol_version == "2026-07-28"
        catalog = await client.list_tools()
        actual = {tool.name: tool.input_schema for tool in catalog.tools}
        expected = {
            tool["name"]: tool["inputSchema"] for tool in service.tool_definitions()
        }
        assert actual == expected
        assert len(actual) == 19
        assert not ({"exec", "eval", "expression", "run_code"} & actual.keys())
        for name, schema in actual.items():
            assert schema["additionalProperties"] is False
            if not name.startswith("get_"):
                assert "expected_revision" in schema["required"]
        result = await client.call_tool("get_scene", {})
        assert not result.is_error
        assert payload(result)["scene"] == service.snapshot()


@pytest.mark.asyncio
async def test_legacy_client_negotiates_supported_handshake():
    async with Client(create_mcp_server(SceneService()), mode="legacy") as client:
        assert client.protocol_version == "2025-11-25"
        result = await client.call_tool("get_scene", {})
        assert not result.is_error


@pytest.mark.asyncio
async def test_mcp_edits_selection_and_manual_undo_share_one_scene():
    service = SceneService()
    async with Client(create_mcp_server(service)) as client:
        change = await client.call_tool(
            "update_geometry",
            {
                "id": "island_ember",
                "parameters": {"radius": 180},
                "expected_revision": 0,
                "request_id": "mcp_shape",
            },
        )
        assert not change.is_error
        assert payload(change)["scene"] == service.snapshot()
        assert service.snapshot()["revision"] == 1
        assert service.snapshot()["history"]["entries"][-1]["actor"] == "mcp"
        selection = await client.call_tool(
            "select",
            {
                "ids": ["island_ember"],
                "expected_revision": 1,
            },
        )
        assert not selection.is_error
        selected = payload(await client.call_tool("get_selection", {}))
        assert selected["selection"] == ["island_ember"]
        assert selected["objects"][0]["parameters"]["radius"] == 180
        service.execute({"op": "undo", "expected_revision": 2}, actor="manual")
        reread = payload(await client.call_tool("get_scene", {}))["scene"]
        assert reread["selection"] == []
        assert reread["revision"] == 3
        assert reread == service.snapshot()


@pytest.mark.asyncio
async def test_mcp_conflicts_validation_and_idempotency_are_truthful():
    service = SceneService()
    async with Client(create_mcp_server(service)) as client:
        args = {
            "expected_revision": 0,
            "request_id": "repeat_once",
            "view": {"grid": True},
        }
        first = payload(await client.call_tool("set_view", args))
        replay = payload(await client.call_tool("set_view", args))
        assert replay["replayed"] is True
        assert replay["transaction_id"] == first["transaction_id"]
        assert service.snapshot()["revision"] == 1
        conflict = await client.call_tool("undo", {"expected_revision": 0})
        assert conflict.is_error
        assert payload(conflict)["error"]["code"] == "revision_conflict"
        invalid = await client.call_tool(
            "create_geometry",
            {
                "expected_revision": 1,
                "parameters": {"radius": -20},
            },
        )
        assert invalid.is_error
        assert payload(invalid)["error"]["code"] == "invalid_arguments"
        missing_revision = await client.call_tool("undo", {})
        assert missing_revision.is_error
        extra = await client.call_tool("get_scene", {"code": "print('not a tool')"})
        assert extra.is_error
        assert service.snapshot()["revision"] == 1


@pytest.mark.asyncio
async def test_mcp_batch_rolls_back_and_undo_redo_are_atomic():
    service = SceneService()
    async with Client(create_mcp_server(service)) as client:
        before = service.snapshot()
        failed = await client.call_tool(
            "batch",
            {
                "expected_revision": 0,
                "commands": [
                    {
                        "op": "set_style",
                        "id": "island_ember",
                        "style": {"palette": "mono"},
                    },
                    {
                        "op": "update_geometry",
                        "id": "absent",
                        "parameters": {"radius": 160},
                    },
                ],
            },
        )
        assert failed.is_error
        assert service.snapshot() == before
        batch = await client.call_tool(
            "batch",
            {
                "expected_revision": 0,
                "commands": [
                    {
                        "op": "set_style",
                        "id": "island_ember",
                        "style": {"palette": "mono"},
                    },
                    {
                        "op": "update_geometry",
                        "id": "island_ember",
                        "parameters": {"radius": 160},
                    },
                ],
            },
        )
        assert not batch.is_error
        edited = service.snapshot()["objects"]
        assert service.snapshot()["revision"] == 1
        assert not (await client.call_tool("undo", {"expected_revision": 1})).is_error
        assert service.snapshot()["objects"] == before["objects"]
        assert not (await client.call_tool("redo", {"expected_revision": 2})).is_error
        assert service.snapshot()["objects"] == edited


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:8000",
        "http://example.com",
        "http://user:pass@localhost:8000",
        "http://localhost:8000/path",
        "http://localhost:8000?forward=http://example.com",
    ],
)
def test_stdio_proxy_rejects_non_loopback_origins(url):
    with pytest.raises(ValueError, match="loopback"):
        RemoteStudioBackend(url)


@pytest.mark.asyncio
async def test_unreachable_stdio_backend_never_creates_a_private_scene():
    async def disconnected(request):
        raise httpx.ConnectError("offline", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(disconnected)) as http:
        proxy = RemoteStudioBackend("http://127.0.0.1:8000", http)
        async with Client(create_mcp_server(proxy)) as client:
            result = await client.call_tool("get_scene", {})
            assert result.is_error
            assert payload(result)["error"]["code"] == "studio_unavailable"
            assert "scene" not in payload(result)


@pytest.fixture
def live_studio():
    from studio.app import create_app

    service = SceneService()
    app = create_app(service=service)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="error", lifespan="on"))
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [sock]}, daemon=True
    )
    thread.start()
    deadline = time.monotonic() + 10
    try:
        while not server.started:
            if not thread.is_alive() or time.monotonic() >= deadline:
                raise RuntimeError("Test studio did not start")
            time.sleep(0.01)
        yield f"http://127.0.0.1:{port}", service
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
        assert not thread.is_alive(), "Test studio did not stop"


@pytest.mark.asyncio
async def test_streamable_http_official_client_uses_running_web_scene(live_studio):
    url, service = live_studio
    async with http_mcp_client(url + "/mcp/") as client:
        assert client.protocol_version == "2026-07-28"
        assert len((await client.list_tools()).tools) == 19
        result = await client.call_tool(
            "set_style",
            {
                "id": "island_ember",
                "style": {"palette": "mono"},
                "expected_revision": 0,
            },
        )
        assert not result.is_error
        async with httpx.AsyncClient(trust_env=False) as http:
            current = (await http.get(url + "/api/scene")).json()
        assert current == payload(result)["scene"] == service.snapshot()
        pose = {
            name: current["objects"][0]["parameters"][name]
            for name in ("x", "y", "radius", "elongation", "rotation", "warp")
        }
        pose["radius"] = 235
        keyed = await client.call_tool(
            "set_keyframe",
            {
                "id": "island_ember",
                "keyframe": {"time": 2, "parameters": pose, "easing": "linear"},
                "expected_revision": 1,
            },
        )
        assert not keyed.is_error
        assert (
            service.get_geometry("island_ember", time_value=2).parameters["radius"]
            == 235
        )
        removed = await client.call_tool(
            "delete_keyframe", {"id": "island_ember", "time": 2, "expected_revision": 2}
        )
        assert not removed.is_error
        assert service.snapshot()["objects"][0]["keyframes"] == []


@pytest.mark.asyncio
async def test_stdio_official_client_proxies_same_http_app(live_studio):
    url, service = live_studio
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "studio.mcp_server", "--studio-url", url],
        cwd=ROOT,
    )
    async with Client(params) as stdio, http_mcp_client(url + "/mcp/") as http_mcp:
        assert stdio.protocol_version == "2026-07-28"
        assert len((await stdio.list_tools()).tools) == 19
        args = {
            "id": "island_lagoon",
            "parameters": {"radius": 155},
            "expected_revision": 0,
            "request_id": "stdio_once",
        }
        changed = payload(await stdio.call_tool("update_geometry", args))
        observed = payload(await http_mcp.call_tool("get_scene", {}))
        assert changed["scene"] == observed["scene"] == service.snapshot()
        replay = payload(await stdio.call_tool("update_geometry", args))
        assert replay["replayed"] is True
        assert replay["scene"]["revision"] == 1
        conflict = await stdio.call_tool("undo", {"expected_revision": 0})
        assert conflict.is_error
        assert payload(conflict)["error"]["code"] == "revision_conflict"
        obj = service.snapshot()["objects"][1]
        pose = {
            name: obj["parameters"][name]
            for name in ("x", "y", "radius", "elongation", "rotation", "warp")
        }
        keyed = await stdio.call_tool(
            "set_keyframe",
            {
                "id": obj["id"],
                "keyframe": {"time": 6, "parameters": pose},
                "expected_revision": 1,
            },
        )
        assert not keyed.is_error
        observed = payload(await http_mcp.call_tool("get_scene", {}))
        assert observed["scene"]["objects"][1]["keyframes"][0]["time"] == 6


@pytest.mark.asyncio
async def test_real_mcp_authors_and_retimes_shared_motion_path(live_studio):
    url, service = live_studio
    recipe = json.loads((ROOT / "examples/tidal_atlas_choreography.json").read_text())
    island = recipe["objects"][0]
    async with (
        http_mcp_client(url + "/mcp/") as client,
        httpx.AsyncClient(trust_env=False) as http,
    ):
        loaded = await client.call_tool(
            "load_recipe", {"recipe": recipe, "expected_revision": 0}
        )
        assert not loaded.is_error
        args = {
            "id": island["id"],
            "time": 3,
            "new_time": 7.5,
            "position": {"x": 550, "y": 150},
            "expected_revision": 1,
            "request_id": "mcp_motion",
        }
        edited = payload(await client.call_tool("edit_keyframe", args))
        observed = payload(await client.call_tool("get_scene", {}))["scene"]
        assert (
            observed
            == edited["scene"]
            == (await http.get(url + "/api/scene")).json()
            == service.snapshot()
        )
        keys = observed["objects"][0]["keyframes"]
        assert [key["time"] for key in keys] == [0, 6, 7.5, 9, 12]
        assert keys[2]["parameters"] == {
            **island["keyframes"][1]["parameters"],
            "x": 550,
            "y": 150,
        }
        assert service.get_geometry(island["id"], time_value=7.5).parameters["x"] == 550
        assert (
            payload(await client.call_tool("edit_keyframe", args))["replayed"] is True
        )
        collision = await client.call_tool(
            "edit_keyframe",
            {"id": island["id"], "time": 7.5, "new_time": 6, "expected_revision": 2},
        )
        assert (
            collision.is_error
            and payload(collision)["error"]["code"] == "keyframe_collision"
        )
        assert service.snapshot() == observed
        undone = await http.post(
            url + "/api/command", json={"op": "undo", "expected_revision": 2}
        )
        assert undone.status_code == 200
        restored = payload(await client.call_tool("get_scene", {}))["scene"]
        assert restored["objects"] == recipe["objects"]


def test_webmcp_registration_contract_and_unsupported_fallback():
    """Browser API mock tests wiring only; it does not assert native browser support."""
    if not shutil.which("node"):
        pytest.skip("Node.js is needed for browser adapter unit checks")

    result = subprocess.run(
        ["node", "tests/studio/webmcp_contract.mjs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.asyncio
async def test_real_mcp_composes_static_fields_and_observes_manual_source_edits(
    live_studio,
):
    url, service = live_studio
    async with (
        http_mcp_client(url + "/mcp/") as client,
        httpx.AsyncClient(trust_env=False) as http,
    ):
        created = payload(
            await client.call_tool(
                "create_blend",
                {
                    "source_a": "island_ember",
                    "source_b": "island_lagoon",
                    "amount": 0.8,
                    "expected_revision": 0,
                    "request_id": "blend_once",
                },
            )
        )
        blend = created["scene"]["blends"][0]
        changed = await http.post(
            url + "/api/command",
            json={
                "op": "update_geometry",
                "id": "island_ember",
                "parameters": {"x": 250},
                "expected_revision": 1,
            },
        )
        assert changed.status_code == 200
        observed = payload(await client.call_tool("get_scene", {}))["scene"]
        assert (
            observed
            == (await http.get(url + "/api/scene")).json()
            == service.snapshot()
        )
        assert observed["objects"][0]["parameters"]["x"] == 250
        assert observed["blends"][0]["source_a"] == "island_ember"
        updated = payload(
            await client.call_tool(
                "update_blend",
                {"id": blend["id"], "operation": "union", "expected_revision": 2},
            )
        )
        assert updated["scene"]["blends"][0]["operation"] == "union"
        removed = payload(
            await client.call_tool(
                "delete_blend", {"id": blend["id"], "expected_revision": 3}
            )
        )
        assert removed["scene"]["blends"] == []
        assert removed["scene"]["objects"] == observed["objects"]
        restored = payload(await client.call_tool("undo", {"expected_revision": 4}))
        assert restored["scene"]["blends"][0]["id"] == blend["id"]


@pytest.mark.asyncio
async def test_real_mcp_layer_order_blend_style_selection_and_manual_undo(live_studio):
    url, service = live_studio
    demo = json.loads(
        (ROOT / "examples/tidal_atlas_layers.json").read_text(encoding="utf-8")
    )
    async with (
        http_mcp_client(url + "/mcp/") as client,
        httpx.AsyncClient(trust_env=False) as http,
    ):
        loaded = payload(
            await client.call_tool(
                "load_recipe", {"recipe": demo, "expected_revision": 0}
            )
        )
        assert loaded["ok"]
        order = list(reversed(loaded["scene"]["layer_order"]))
        edited = payload(
            await client.call_tool(
                "batch",
                {
                    "commands": [
                        {"op": "reorder_layers", "order": order},
                        {
                            "op": "set_style",
                            "id": "blend_confluence",
                            "style": {"opacity": 0.35, "palette": "mono"},
                        },
                        {"op": "select", "ids": ["blend_confluence"]},
                    ],
                    "expected_revision": 1,
                    "request_id": "layers_once",
                },
            )
        )
        assert edited["scene"]["layer_order"] == order
        selection = payload(await client.call_tool("get_selection", {}))
        assert selection["objects"][0]["style"]["opacity"] == 0.35
        observed = payload(await client.call_tool("get_scene", {}))["scene"]
        assert (
            observed
            == (await http.get(url + "/api/scene")).json()
            == service.snapshot()
        )
        invalid = await client.call_tool(
            "reorder_layers", {"order": order[:-1], "expected_revision": 2}
        )
        assert invalid.is_error and service.snapshot() == observed
        undone = await http.post(
            url + "/api/command", json={"op": "undo", "expected_revision": 2}
        )
        assert undone.status_code == 200
        assert (
            payload(await client.call_tool("get_scene", {}))["scene"]["layer_order"]
            == demo["layer_order"]
        )
