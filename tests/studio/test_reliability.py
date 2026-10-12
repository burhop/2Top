"""Final-candidate invariants, process history reset and Unicode safety."""

import json

import pytest
from fastapi.testclient import TestClient

from studio.app import create_app
from studio.service import SceneError, SceneService


def apply(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


def setup_case(path, kind):
    service = SceneService(path)
    apply(service, "set_style", id="island_ember", style={"opacity": 0.8})
    target = service.snapshot()["objects"][0]["id"]
    if kind == "blend":
        target = apply(
            service, "create_blend", source_a="island_ember", source_b="island_lagoon"
        )["scene"]["blends"][0]["id"]
    return service, target


def commands_for(scene, target, case):
    remaining = [key for key in scene["layer_order"] if key != target]
    order = {
        "omitted_target": remaining,
        "duplicated_deleted_target": [target, target, *remaining],
        "missing_survivor": remaining[:-1],
        "unknown_survivor": remaining[:-1] + ["missing"],
        "duplicated_survivor": remaining[:-1] + [remaining[0]],
    }[case]
    op = (
        "delete_blend"
        if any(b["id"] == target for b in scene["blends"])
        else "delete_geometry"
    )
    return [
        {"op": "reorder_layers", "order": order},
        {"op": "select", "ids": [target]},
        {"op": op, "id": target},
    ]


@pytest.mark.parametrize("kind", ["geometry", "blend"])
@pytest.mark.parametrize(
    "case",
    [
        "omitted_target",
        "duplicated_deleted_target",
        "missing_survivor",
        "unknown_survivor",
        "duplicated_survivor",
    ],
)
def test_final_candidate_order_delete_is_atomic_and_undoable(tmp_path, kind, case):
    service, target = setup_case(tmp_path / "scene.json", kind)
    before = service.snapshot()
    disk = service._storage.read_bytes()
    valid = case in {"omitted_target", "duplicated_deleted_target"}
    if not valid:
        with pytest.raises(SceneError) as error:
            apply(
                service,
                "batch",
                request_id="batch_order_once",
                commands=commands_for(before, target, case),
            )
        assert error.value.code == "validation_error"
        assert service.snapshot() == before and service._storage.read_bytes() == disk
        # Failed intent did not reserve its retry key; a corrected intent is valid.
        case = "omitted_target"
    result = apply(
        service,
        "batch",
        request_id="batch_order_once",
        commands=commands_for(before, target, case),
    )
    after = result["scene"]
    assert after["revision"] == before["revision"] + 1
    assert (
        after["history"]["session_commits"] == before["history"]["session_commits"] + 1
    )
    assert after["layer_order"] == [
        key for key in before["layer_order"] if key != target
    ]
    assert after["selection"] == []
    assert not any(o["id"] == target for o in [*after["objects"], *after["blends"]])
    restored = apply(service, "undo")["scene"]
    for field in ["objects", "blends", "layer_order", "selection"]:
        assert restored[field] == before[field]
    assert SceneService(service._storage).recipe() == service.recipe()
    apply(service, "redo")
    assert service.recipe()["layer_order"] == after["layer_order"]


@pytest.mark.parametrize("kind", ["geometry", "blend"])
def test_http_order_delete_valid_completion_and_structured_invalid_rollback(
    tmp_path, kind
):
    service, target = setup_case(tmp_path / "scene.json", kind)
    before = service.snapshot()
    disk = service._storage.read_bytes()
    with TestClient(
        create_app(service, enable_mcp=False),
        base_url="http://localhost",
        raise_server_exceptions=False,
    ) as client:
        failed = client.post(
            "/api/command",
            json={
                "op": "batch",
                "expected_revision": before["revision"],
                "commands": commands_for(before, target, "unknown_survivor"),
            },
        )
        assert (
            failed.status_code == 400
            and failed.json()["error"]["code"] == "validation_error"
        )
        assert service.snapshot() == before and service._storage.read_bytes() == disk
        completed = client.post(
            "/api/command",
            json={
                "op": "batch",
                "expected_revision": before["revision"],
                "commands": commands_for(before, target, "omitted_target"),
            },
        )
        assert completed.status_code == 200 and completed.json()["ok"]
        assert client.get("/api/scene").status_code == 200


def test_selection_uses_actual_records_not_transient_order_and_failed_batch_retains_redo(
    tmp_path,
):
    service = SceneService(tmp_path / "scene.json")
    apply(service, "set_style", id="island_ember", style={"opacity": 0.8})
    apply(service, "undo")
    before = service.snapshot()
    disk = service._storage.read_bytes()
    ids = before["layer_order"]
    with pytest.raises(SceneError) as error:
        apply(
            service,
            "batch",
            commands=[
                {"op": "reorder_layers", "order": ["missing", *ids]},
                {"op": "select", "ids": ["missing"]},
                {"op": "reorder_layers", "order": ids},
            ],
        )
    assert error.value.code == "object_not_found"
    assert service.snapshot() == before and service._storage.read_bytes() == disk
    assert before["history"]["can_redo"]


def test_restart_preserves_document_revision_geometry_but_changes_session_and_clears_history(
    tmp_path,
):
    service = SceneService(tmp_path / "scene.json")
    apply(service, "set_style", id="island_ember", style={"opacity": 0.8})
    before = service.snapshot()
    restarted = SceneService(service._storage)
    after = restarted.snapshot()
    assert (
        after["document_id"] == before["document_id"]
        and after["revision"] == before["revision"]
    )
    assert after["session_id"] != before["session_id"]
    assert (
        restarted.recipe() == service.recipe()
        and "session_id" not in restarted.recipe()
    )
    assert (
        after["history"]["entries"] == [] and after["history"]["session_commits"] == 0
    )
    assert not after["history"]["can_undo"] and not after["history"]["can_redo"]


@pytest.mark.parametrize("escape", ["\\ud800", "\\udfff"])
@pytest.mark.parametrize("field", ["name", "title", "label"])
def test_invalid_unicode_is_already_rejected_before_http_mutation(
    tmp_path, escape, field
):
    service = SceneService(tmp_path / "scene.json")
    apply(service, "set_style", id="island_ember", style={"opacity": 0.8})
    before = service.snapshot()
    disk = service._storage.read_bytes()
    if field == "name":
        command = {
            "op": "create_geometry",
            "expected_revision": before["revision"],
            "name": "PLACEHOLDER",
        }
    elif field == "title":
        command = {
            "op": "load_recipe",
            "expected_revision": before["revision"],
            "recipe": {**service.recipe(), "title": "PLACEHOLDER"},
        }
    else:
        command = {
            "op": "batch",
            "expected_revision": before["revision"],
            "label": "PLACEHOLDER",
            "commands": [
                {"op": "set_style", "id": "island_ember", "style": {"opacity": 0.5}}
            ],
        }
    raw = json.dumps(command).replace("PLACEHOLDER", escape).encode("ascii")
    with pytest.raises(SceneError) as error:
        service.execute(json.loads(raw))
    assert error.value.code == "validation_error"
    with TestClient(
        create_app(service, enable_mcp=False), base_url="http://localhost"
    ) as client:
        result = client.post(
            "/api/command", content=raw, headers={"Content-Type": "application/json"}
        )
        assert (
            result.status_code == 400
            and result.json()["error"]["code"] == "validation_error"
        )
        assert client.get("/api/scene").status_code == 200
    assert service.snapshot() == before and service._storage.read_bytes() == disk


def test_valid_supplementary_unicode_survives_http_and_disk(tmp_path):
    service = SceneService(tmp_path / "scene.json")
    raw = b'{"op":"create_geometry","expected_revision":0,"name":"\\ud83c\\udf0a"}'
    with TestClient(
        create_app(service, enable_mcp=False), base_url="http://localhost"
    ) as client:
        result = client.post(
            "/api/command", content=raw, headers={"Content-Type": "application/json"}
        )
        assert (
            result.status_code == 200
            and result.json()["scene"]["objects"][-1]["name"] == "\U0001f30a"
        )
    assert (
        SceneService(service._storage).recipe()["objects"][-1]["name"] == "\U0001f30a"
    )
