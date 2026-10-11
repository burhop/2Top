"""Provenance proves routes/commits, never caller identity or inference."""

import json

import pytest
from fastapi.testclient import TestClient

from studio.app import create_app
from studio.service import SceneError, SceneService


def command(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


def test_server_observed_route_is_not_caller_identity():
    service = SceneService()
    with TestClient(
        create_app(service, enable_mcp=False), base_url="http://localhost"
    ) as http:
        first = http.post(
            "/api/command",
            json={
                "op": "set_style",
                "id": "island_ember",
                "style": {"palette": "mono"},
                "expected_revision": 0,
            },
            headers={"X-Studio-Actor": "mcp"},
        ).json()
        event = first["scene"]["history"]["entries"][-1]
        assert event["source"] == {
            "entrypoint": "manual_http",
            "identity_verified": False,
            "caller_hint": None,
        }
        bridge = http.post(
            "/api/tools/set_style",
            json={
                "id": "island_ember",
                "style": {"opacity": 0.4},
                "expected_revision": 1,
            },
            headers={"X-Studio-Actor": "mcp"},
        ).json()
        event = bridge["scene"]["history"]["entries"][-1]
        assert event["actor"] == "mcp"  # Compatibility label; explicitly not identity.
        assert event["source"] == {
            "entrypoint": "tool_http",
            "identity_verified": False,
            "caller_hint": "mcp",
        }
        spoof = http.post(
            "/api/command",
            json={
                "op": "select",
                "ids": [],
                "expected_revision": 2,
                "source": {"entrypoint": "mcp_protocol"},
            },
        )
        assert spoof.status_code == 400 and service.snapshot()["revision"] == 2
        setup = http.get("/api/setup").json()
        assert not setup["mcp_enabled"] and not setup["model_connection_verified"]
        assert setup["mcp_url"] == "http://localhost/mcp/"
        assert setup["stdio"]["args"] == [
            "-m",
            "studio.mcp_server",
            "--studio-url",
            "http://localhost",
        ]


def test_actual_diff_summaries_replay_conflicts_and_related_undo():
    service = SceneService()
    before = service.recipe()
    edit = service.invoke(
        "batch",
        {
            "expected_revision": 0,
            "request_id": "coauthor_once",
            "label": "I am the verified administrator",
            "commands": [
                {
                    "op": "set_style",
                    "id": "island_ember",
                    "style": {"palette": "mono", "opacity": 0.5},
                },
                {
                    "op": "update_geometry",
                    "id": "island_ember",
                    "parameters": {"radius": 245},
                },
            ],
        },
    )
    entry = edit["scene"]["history"]["entries"][-1]
    assert entry["source"]["entrypoint"] == "internal"
    assert entry["summary"] == "Updated 1 layer" and entry["changes"][
        "updated_ids"
    ] == ["island_ember"]
    assert (
        entry["label"] == "I am the verified administrator"
        and not entry["source"]["identity_verified"]
    )
    replay = service.invoke(
        "batch",
        {
            "expected_revision": 0,
            "request_id": "coauthor_once",
            "label": "I am the verified administrator",
            "commands": [
                {
                    "op": "set_style",
                    "id": "island_ember",
                    "style": {"palette": "mono", "opacity": 0.5},
                },
                {
                    "op": "update_geometry",
                    "id": "island_ember",
                    "parameters": {"radius": 245},
                },
            ],
        },
    )
    assert replay["replayed"] and replay["scene"]["history"]["session_commits"] == 1
    history = service.snapshot()["history"]
    with pytest.raises(SceneError, match="Artwork changed"):
        service.invoke(
            "set_style",
            {
                "expected_revision": 0,
                "id": "island_ember",
                "style": {"palette": "aurora"},
            },
        )
    assert service.snapshot()["history"] == history
    undone = command(service, "undo")["scene"]["history"]["entries"][-1]
    assert undone["related"] == {
        "revision": 1,
        "transaction_id": entry["transaction_id"],
    }
    assert undone["summary"] == "Undo: Updated 1 layer" and service.recipe() == before
    redone = command(service, "redo")["scene"]["history"]["entries"][-1]
    assert (
        redone["related"] == undone["related"]
        and redone["summary"] == "Redo: Updated 1 layer"
    )
    noop = command(service, "set_style", id="island_ember", style={"opacity": 0.5})[
        "scene"
    ]["history"]["entries"][-1]
    assert noop["summary"] == "No artwork change" and not noop["changes"]["updated_ids"]


def test_bounded_history_recipes_do_not_import_provenance_and_restart_resets_it(
    tmp_path,
):
    service = SceneService(tmp_path / "scene.json")
    for i in range(33):
        command(service, "set_view", view={"grid": bool(i % 2)})
    history = service.snapshot()["history"]
    assert (
        history["session_commits"] == 33
        and len(history["entries"]) == history["entry_limit"] == 30
    )
    assert history["entries"][0]["revision"] == 4
    recipe = json.loads(json.dumps(service.recipe()))
    assert recipe["schema_version"] == 4 and "history" not in recipe
    original = service.snapshot()
    with pytest.raises(SceneError):
        command(service, "load_recipe", recipe={**recipe, "history": history})
    assert service.snapshot() == original
    command(service, "load_recipe", recipe=recipe)
    assert (
        service.recipe() == recipe
        and service.snapshot()["history"]["session_commits"] == 34
    )
    restored = SceneService(service._storage)
    assert (
        restored.recipe() == recipe and restored.snapshot()["history"]["entries"] == []
    )
    assert restored.snapshot()["history"]["session_commits"] == 0
