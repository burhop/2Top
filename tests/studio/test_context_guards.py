import pytest
from fastapi.testclient import TestClient

from studio.app import create_app
from studio.service import SceneError, SceneService


def guarded(scene, **extra):
    return {
        "op": "set_view",
        "view": {"contours": 30},
        "expected_revision": scene["revision"],
        "expected_document_id": scene["document_id"],
        "expected_session_id": scene["session_id"],
        **extra,
    }


def test_new_document_with_equal_revision_cannot_accept_old_command_or_retry_key():
    old = SceneService().snapshot()
    service = SceneService()
    before = service.snapshot()
    assert old["revision"] == before["revision"]
    with pytest.raises(SceneError) as error:
        service.execute(guarded(old, request_id="old-context"))
    assert error.value.code == "document_conflict" and error.value.status == 409
    assert service.snapshot() == before
    assert service.execute(guarded(before, request_id="old-context"))["ok"]


def test_persisted_restart_same_document_revision_rejects_old_session(tmp_path):
    path = tmp_path / "scene.json"
    original = SceneService(path)
    original.execute({"op": "set_view", "view": {}, "expected_revision": 0})
    old = original.snapshot()
    service = SceneService(path)
    before = service.snapshot()
    disk = path.read_bytes()
    assert (
        old["document_id"] == before["document_id"]
        and old["revision"] == before["revision"]
        and old["session_id"] != before["session_id"]
    )
    with pytest.raises(SceneError) as error:
        service.execute(guarded(old, request_id="restart-context"))
    assert (
        error.value.code == "session_conflict"
        and service.snapshot() == before
        and path.read_bytes() == disk
    )
    assert service.execute(guarded(before, request_id="restart-context"))["ok"]


def test_matching_guards_replay_stale_revision_and_legacy_calls_remain_compatible():
    service = SceneService()
    before = service.snapshot()
    command = guarded(before, request_id="guarded-once")
    changed = service.execute(command)
    assert changed["scene"]["revision"] == before["revision"] + 1
    assert service.execute(command)["replayed"] is True
    assert service.execute(
        {"op": "undo", "expected_revision": changed["scene"]["revision"]}
    )["ok"]
    assert service.execute(command)["replayed"] is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_document_id", True),
        ("expected_document_id", 42),
        ("expected_document_id", ""),
        ("expected_session_id", True),
        ("expected_session_id", "../invalid"),
        ("expected_session_id", "x" * 200),
    ],
)
def test_invalid_context_guards_are_data_validation_errors_without_mutations(
    field, value
):
    service = SceneService()
    before = service.snapshot()
    with pytest.raises(SceneError) as error:
        service.execute(guarded(before, **{field: value}))
    assert error.value.code == "validation_error" and service.snapshot() == before


def test_http_schema_exposes_optional_guards_and_rejects_mismatched_context():
    service = SceneService()
    with TestClient(
        create_app(service, enable_mcp=False), base_url="http://localhost"
    ) as client:
        schema = next(
            tool
            for tool in client.get("/api/tools").json()
            if tool["name"] == "set_view"
        )["inputSchema"]
        assert (
            "expected_document_id" in schema["properties"]
            and "expected_session_id" in schema["properties"]
        )
        assert "expected_document_id" not in schema["required"]
        before = service.snapshot()
        result = client.post(
            "/api/command", json=guarded(before, expected_session_id="session_retired")
        )
        assert (
            result.status_code == 409
            and result.json()["error"]["code"] == "session_conflict"
            and service.snapshot() == before
        )
