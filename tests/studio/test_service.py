"""Transaction, persistence and security contracts shared by all editing paths."""

import concurrent.futures
import json

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from studio.app import create_app
from studio.service import SceneError, SceneService, tool_definitions


def apply(service, op, **kwargs):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **kwargs}
    )


def test_create_update_selection_and_cross_actor_undo():
    s = SceneService()
    result = apply(s, "create_geometry", name="Human island")
    object_id = result["affected_ids"][0]
    assert s.snapshot()["selection"] == [object_id]
    s.invoke(
        "update_geometry",
        {"id": object_id, "parameters": {"warp": 0.8}, "expected_revision": 1},
        actor="mcp",
    )
    assert s.snapshot()["objects"][-1]["parameters"]["warp"] == 0.8
    assert s.snapshot()["history"]["entries"][-1]["actor"] == "mcp"
    apply(s, "undo")
    assert s.snapshot()["objects"][-1]["parameters"]["warp"] == 0.5
    apply(s, "redo")
    assert s.snapshot()["objects"][-1]["parameters"]["warp"] == 0.8
    assert s.snapshot()["revision"] == 4


def test_atomic_batch_rolls_back_all_children():
    s = SceneService()
    before = s.snapshot()
    with pytest.raises(SceneError, match="Unknown island"):
        apply(
            s,
            "batch",
            commands=[
                {"op": "create_geometry"},
                {
                    "op": "update_geometry",
                    "id": "missing",
                    "parameters": {"radius": 200},
                },
            ],
        )
    assert s.snapshot() == before
    result = apply(
        s,
        "batch",
        commands=[
            {"op": "create_geometry", "name": "One"},
            {"op": "create_geometry", "name": "Two"},
        ],
    )
    assert len(result["scene"]["objects"]) == 5
    apply(s, "undo")
    assert len(s.snapshot()["objects"]) == 3


@pytest.mark.parametrize(
    "command",
    [
        {"op": "create_geometry", "parameters": {"radius": -1}},
        {"op": "create_geometry", "parameters": {"radius": float("nan")}},
        {"op": "create_geometry", "parameters": {"x": float("inf")}},
        {"op": "create_geometry", "parameters": {"lobes": 3.1}},
        {"op": "create_geometry", "parameters": {"callback": "eval('bad')"}},
        {"op": "create_geometry", "surprise": True},
        {"op": "set_view", "view": {"contours": 100000}},
        {"op": "batch", "commands": [{"op": "undo"}]},
        {
            "op": "batch",
            "commands": [{"op": "create_geometry", "expected_revision": 0}],
        },
        {"op": "update_geometry", "id": "island_ember", "parameters": {"radius": None}},
    ],
)
def test_invalid_commands_never_mutate(command):
    s = SceneService()
    before = s.snapshot()
    with pytest.raises(SceneError):
        s.execute({"expected_revision": 0, **command})
    assert s.snapshot() == before


def test_optimistic_concurrency_and_idempotent_retries():
    s = SceneService()
    command = {
        "op": "create_geometry",
        "expected_revision": 0,
        "request_id": "retry-me",
    }
    first = s.execute(command)
    again = s.execute(command)
    assert again["replayed"]
    assert first["transaction_id"] == again["transaction_id"]
    assert len(s.snapshot()["objects"]) == 4
    with pytest.raises(SceneError) as conflict:
        s.execute({"op": "create_geometry", "expected_revision": 0})
    assert conflict.value.code == "revision_conflict"
    with pytest.raises(SceneError) as reused:
        s.execute({**command, "name": "Changed"})
    assert reused.value.code == "request_id_reused"
    apply(s, "create_geometry")
    assert (
        s.execute(command)["scene"]["revision"] == 2
    )  # never send an old snapshot on retry


def test_two_concurrent_writers_do_not_lose_updates():
    s = SceneService()

    def create(_):
        try:
            s.execute({"op": "create_geometry", "expected_revision": 0})
            return "ok"
        except SceneError as error:
            return error.code

    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        results = list(pool.map(create, range(2)))
    assert sorted(results) == ["ok", "revision_conflict"]
    assert s.snapshot()["revision"] == 1


def test_recipe_roundtrip_duplicate_ids_and_no_callbacks(tmp_path):
    s = SceneService(tmp_path / "scene.json")
    apply(s, "create_geometry", parameters={"phase": 1.4, "warp": 0.82})
    restored = SceneService(tmp_path / "scene.json")
    assert restored.recipe() == s.recipe()
    assert restored.snapshot()["document_id"] == s.snapshot()["document_id"]
    recipe = json.loads(json.dumps(s.recipe()))
    apply(s, "load_recipe", recipe=recipe)
    assert s.recipe() == recipe
    recipe["objects"][1]["id"] = recipe["objects"][0]["id"]
    with pytest.raises(SceneError) as failure:
        apply(s, "load_recipe", recipe=recipe)
    assert failure.value.code == "duplicate_id"


def test_storage_failure_does_not_commit(tmp_path):
    path = tmp_path / "not-a-directory"
    path.write_text("x")
    s = SceneService(path / "scene.json")
    before = s.snapshot()
    with pytest.raises(SceneError) as error:
        apply(s, "create_geometry")
    assert error.value.code == "storage_error"
    assert s.snapshot() == before


def test_undo_redo_branch_and_bounded_scene():
    s = SceneService()
    apply(s, "create_geometry")
    apply(s, "undo")
    apply(s, "create_geometry")
    assert not s.snapshot()["history"]["can_redo"]
    for _ in range(12):
        apply(s, "create_geometry")
    with pytest.raises(SceneError) as error:
        apply(s, "create_geometry")
    assert error.value.code == "object_limit"
    assert len(s.snapshot()["objects"]) == 16


def test_snapshot_is_a_deep_copy():
    s = SceneService()
    snapshot = s.snapshot()
    snapshot["objects"][0]["parameters"]["radius"] = -100
    assert s.snapshot()["objects"][0]["parameters"]["radius"] > 0


def test_public_schemas_are_valid_and_match_commands():
    definitions = tool_definitions()
    assert len(definitions) == 21
    for definition in definitions:
        Draft202012Validator.check_schema(definition["inputSchema"])
        assert "op" not in definition["inputSchema"].get("properties", {})
    create = next(d for d in definitions if d["name"] == "create_geometry")
    Draft202012Validator(create["inputSchema"]).validate(
        {"expected_revision": 0, "parameters": {"warp": 0.3}}
    )


def test_http_and_tool_requests_share_authoritative_scene():
    s = SceneService()
    with TestClient(
        create_app(s, enable_mcp=False), base_url="http://localhost"
    ) as client:
        original = client.get("/api/scene").json()
        result = client.post(
            "/api/command",
            json={
                "op": "create_geometry",
                "expected_revision": original["revision"],
                "name": "Manual",
            },
        )
        assert result.status_code == 200
        tool = client.post("/api/tools/get_scene", json={}).json()
        assert tool["scene"]["objects"][-1]["name"] == "Manual"
        island = result.json()["affected_ids"][0]
        edited = client.post(
            "/api/tools/update_geometry",
            json={"expected_revision": 1, "id": island, "parameters": {"warp": 0.9}},
            headers={"x-studio-actor": "mcp"},
        )
        assert edited.status_code == 200
        assert (
            client.get("/api/scene").json()["objects"][-1]["parameters"]["warp"] == 0.9
        )
        conflict = client.post(
            "/api/command", json={"op": "undo", "expected_revision": 0}
        )
        assert conflict.status_code == 409
        assert conflict.json()["error"]["code"] == "revision_conflict"
        assert client.post("/api/command", content="{broken").status_code == 400
        assert (
            client.post("/api/tools/get_scene", json={"unexpected": True}).status_code
            == 400
        )
        assert (
            client.get(
                "/api/scene", headers={"origin": "https://evil.example"}
            ).status_code
            == 403
        )
        assert (
            client.get("/api/scene", headers={"host": "evil.example"}).status_code
            == 400
        )


def test_playback_clock_is_shared_and_read_only(monkeypatch):
    import studio.service as module

    clock = [100.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    s = SceneService()
    apply(s, "set_view", animation={"playing": True, "speed": 1, "time": 2})
    clock[0] += 3
    assert s.snapshot()["animation"]["time"] == 5
    assert s.invoke("get_scene", {})["scene"]["animation"]["time"] == 5
    assert s.snapshot()["revision"] == 1
    apply(s, "set_style", id="island_ember", style={"palette": "mono"})
    clock[0] += 2
    assert s.snapshot()["animation"]["time"] == 7
    apply(s, "set_view", animation={"playing": False})
    clock[0] += 15
    assert s.snapshot()["animation"]["time"] == 7


@pytest.mark.parametrize("parameters", [{"x": True}, {"radius": "200"}, {"warp": None}])
def test_geometry_types_are_not_silently_coerced(parameters):
    s = SceneService()
    with pytest.raises(SceneError):
        apply(s, "create_geometry", parameters=parameters)
    assert s.snapshot()["revision"] == 0


def test_api_rejects_nonfinite_json_with_truthful_error():
    with TestClient(
        create_app(enable_mcp=False), base_url="http://localhost"
    ) as client:
        response = client.post(
            "/api/command",
            content='{"op":"create_geometry","expected_revision":0,"parameters":{"x":NaN}}',
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_json"
        assert client.get("/api/scene").json()["revision"] == 0
        assert client.get("/api/docs").status_code == 200


def test_chunked_request_cannot_bypass_body_limit():
    with TestClient(
        create_app(enable_mcp=False), base_url="http://localhost"
    ) as client:
        data = b'{"op":"select","expected_revision":0,"ids":[]' + b" " * 600_000 + b"}"
        response = client.post("/api/command", content=(chunk for chunk in [data]))
        assert response.status_code == 413
        assert response.json()["error"]["code"] == "request_too_large"
        assert client.get("/api/scene").json()["revision"] == 0
        nested = '{"x":' + "[" * 2000 + "1" + "]" * 2000 + "}"
        assert client.post("/api/command", content=nested).status_code == 400


def test_null_patches_are_rejected_by_schema_before_replay_lookup():
    from jsonschema import ValidationError

    s = SceneService()
    args = {
        "id": "island_ember",
        "parameters": {},
        "expected_revision": 0,
        "request_id": "nullable-retry",
    }
    s.invoke("update_geometry", args)
    changed = {**args, "parameters": {"radius": None}}
    schema = next(
        tool for tool in tool_definitions() if tool["name"] == "update_geometry"
    )["inputSchema"]
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(changed)
    with pytest.raises(SceneError) as error:
        s.invoke("update_geometry", changed)
    assert error.value.code == "validation_error"
    assert s.snapshot()["revision"] == 1


def test_scene_snapshot_exposes_real_reusable_engine_objects():
    import numpy as np
    from geometry import BaseField, ImplicitCurve

    s = SceneService()
    field = s.get_geometry("island_ember", time_value=2)
    assert isinstance(field, BaseField)
    manager = s.geometry_scene(time_value=2)
    curve = manager.get_object("island_ember")
    assert isinstance(curve, ImplicitCurve)
    paths = s.geometry_paths(resolution=80, time_value=2)
    points = np.asarray(paths["paths"]["island_ember"]["points"])
    assert len(points) == 81
    np.testing.assert_allclose(
        field.evaluate(points[:, 0], points[:, 1]), 0, atol=1e-12
    )
    assert paths["revision"] == 0
    assert paths["document_id"] == s.snapshot()["document_id"]
    before = field.to_dict()
    apply(s, "update_geometry", id="island_ember", parameters={"radius": 300})
    assert field.to_dict() == before  # detached snapshot never edits live scene
    assert s.get_geometry("island_ember", 2).to_dict() != before
    assert s.geometry_paths(80, 2)["revision"] == 1


def test_engine_path_api_is_bounded_and_observes_authoritative_edits():
    with TestClient(
        create_app(enable_mcp=False), base_url="http://localhost"
    ) as client:
        response = client.get("/api/geometry?resolution=72&time=3")
        assert response.status_code == 200
        body = response.json()
        assert len(body["paths"]) == 3
        assert body["revision"] == 0
        assert all(len(item["points"]) == 73 for item in body["paths"].values())
        assert client.get("/api/geometry?resolution=100000").status_code == 422
        assert client.get("/api/geometry?time=NaN").status_code == 422
        assert client.get("/api/scene").json()["revision"] == 0
