import json
from pathlib import Path
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient
from geometry.choreography import POSE_FIELDS

from studio.app import create_app
from studio.retiming import retimed_islands
from studio.service import SceneError, SceneService

ROOT = Path(__file__).resolve().parents[2]


def apply(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


@pytest.fixture
def authored(tmp_path):
    service = SceneService(tmp_path / "scene.json")
    recipe = json.loads((ROOT / "examples/tidal_atlas_choreography.json").read_text())
    for island in recipe["objects"]:
        for key, time in zip(island["keyframes"], [1, 3, 6, 9, 11]):
            key["time"] = time
    apply(service, "load_recipe", recipe=recipe)
    return service


@pytest.mark.parametrize(
    "times,delta,expected",
    [
        ([1, 3], -1, [0, 2, 6, 9, 11]),
        ([9, 11], 1, [1, 3, 6, 10, 12]),
        ([3, 6], 4, [1, 7, 9, 10, 11]),
        ([11, 9, 6, 3, 1], 1, [2, 4, 7, 10, 12]),
    ],
)
def test_shared_shift_preserves_every_pose_and_other_scene_fields(
    authored, times, delta, expected
):
    before = authored.snapshot()
    obj = before["objects"][0]
    after = apply(
        authored,
        "retime_keyframes",
        targets=[{"id": obj["id"], "times": times}],
        delta=delta,
    )["scene"]
    changed = after["objects"][0]
    assert [key["time"] for key in changed["keyframes"]] == expected
    assert (
        changed["parameters"] == obj["parameters"] and changed["style"] == obj["style"]
    )
    for original in obj["keyframes"]:
        destination = (
            original["time"] + delta if original["time"] in times else original["time"]
        )
        assert next(k for k in changed["keyframes"] if k["time"] == destination) == {
            **original,
            "time": destination,
        }
    for field in ["animation", "selection", "view", "blends", "layer_order", "title"]:
        assert after[field] == before[field]
    assert after["objects"][1:] == before["objects"][1:]


def test_selected_times_vacate_together_and_target_order_is_irrelevant(authored):
    recipe = authored.recipe()
    for island in recipe["objects"]:
        island["keyframes"][2]["time"] = 5
    apply(authored, "load_recipe", recipe=recipe)
    before = authored.snapshot()
    targets = [{"id": o["id"], "times": [5, 1, 3]} for o in before["objects"][:2]]
    a = retimed_islands(before, targets, 2)
    b = retimed_islands(before, list(reversed(targets)), 2)
    assert {o["id"]: o for o in a} == {o["id"]: o for o in b}
    result = apply(authored, "retime_keyframes", targets=targets, delta=2)
    assert result["scene"]["revision"] == before["revision"] + 1
    assert len(result["affected_ids"]) == 2
    for obj in result["scene"]["objects"][:2]:
        assert [k["time"] for k in obj["keyframes"]] == [3, 5, 7, 9, 11]


@pytest.mark.parametrize(
    "args",
    [
        {"targets": []},
        {"targets": [{"id": "island_solstice", "times": []}]},
        {"targets": [{"id": "island_solstice", "times": [3, 3]}]},
        {"targets": [{"id": "island_solstice", "times": [True]}]},
        {"targets": [{"id": "island_solstice", "times": ["3"]}]},
        {"targets": [{"id": "island_solstice", "times": [-1]}]},
        {"targets": [{"id": "island_solstice", "times": [13]}]},
        {"targets": [{"id": "island_solstice", "times": list(range(25))}]},
        {"targets": [{"id": "island_solstice", "times": [3]}] * 2},
        {"targets": [{"id": f"island_{i}", "times": [3]} for i in range(17)]},
        {"delta": True},
        {"delta": "1"},
        {"delta": float("inf")},
        {"delta": float("nan")},
        {"delta": 12.01},
        {"delta": -12.01},
        {"extra": "forbidden"},
    ],
)
def test_malformed_args_leave_revision_disk_history_and_retry_keys_unchanged(
    authored, args
):
    before = authored.snapshot()
    disk = authored._storage.read_bytes()
    command = {
        "op": "retime_keyframes",
        "expected_revision": before["revision"],
        "request_id": "bad-retime",
        "targets": [{"id": before["objects"][0]["id"], "times": [3, 6]}],
        "delta": 1,
        **args,
    }
    with pytest.raises(SceneError) as error:
        authored.execute(command)
    assert error.value.code == "validation_error"
    assert authored.snapshot() == before and authored._storage.read_bytes() == disk
    command.update(targets=[{"id": before["objects"][0]["id"], "times": [3]}], delta=1)
    command.pop("extra", None)
    assert authored.execute(command)["ok"]


@pytest.mark.parametrize(
    "times,delta,code",
    [
        ([3, 6], 3, "keyframe_collision"),
        ([1], -1.01, "keyframe_range"),
        ([11], 1.01, "keyframe_range"),
        ([2], 1, "keyframe_not_found"),
    ],
)
def test_any_second_track_failure_rejects_the_complete_operation(
    authored, times, delta, code
):
    before = authored.snapshot()
    targets = [
        {"id": before["objects"][0]["id"], "times": [3]},
        {"id": before["objects"][1]["id"], "times": times},
    ]
    # First track is valid even when the second collides.
    if delta == 3:
        targets[0]["times"] = [1]
    disk = authored._storage.read_bytes()
    with pytest.raises(SceneError) as error:
        apply(
            authored,
            "retime_keyframes",
            targets=targets,
            delta=delta,
            request_id="failed-target",
        )
    assert error.value.code == code
    assert authored.snapshot() == before and authored._storage.read_bytes() == disk


def test_exact_endpoints_and_all_24_keys_across_all_16_islands():
    service = SceneService()
    for i in range(13):
        apply(service, "create_geometry", name=f"Motion {i}")
    recipe = service.recipe()
    for obj in recipe["objects"]:
        obj["keyframes"] = [
            {
                "time": i / 2,
                "parameters": {name: obj["parameters"][name] for name in POSE_FIELDS},
                "easing": "linear",
            }
            for i in range(24)
        ]
    apply(service, "load_recipe", recipe=recipe)
    targets = [
        {"id": obj["id"], "times": [k["time"] for k in obj["keyframes"]]}
        for obj in recipe["objects"]
    ]
    after = apply(service, "retime_keyframes", targets=targets, delta=0.5)["scene"]
    assert len(after["objects"]) == 16
    assert all(
        [key["time"] for key in obj["keyframes"]] == [i / 2 + 0.5 for i in range(24)]
        for obj in after["objects"]
    )


def test_persistence_undo_redo_replay_stale_and_batch_rollback(authored, monkeypatch):
    before = authored.snapshot()
    target = {"id": before["objects"][0]["id"], "times": [3, 6]}
    command = {
        "op": "retime_keyframes",
        "targets": [target],
        "delta": 1.5,
        "expected_revision": before["revision"],
        "request_id": "retime-once",
    }
    changed = authored.execute(command)
    assert authored.execute(command)["replayed"] is True
    assert SceneService(authored._storage).recipe() == authored.recipe()
    apply(authored, "undo")
    assert authored.recipe()["objects"] == before["objects"]
    apply(authored, "redo")
    assert authored.recipe()["objects"] == changed["scene"]["objects"]
    snapshot, disk = authored.snapshot(), authored._storage.read_bytes()
    with pytest.raises(SceneError) as conflict:
        authored.execute({**command, "request_id": "stale-retime"})
    assert (
        conflict.value.code == "revision_conflict" and authored.snapshot() == snapshot
    )
    with pytest.raises(SceneError):
        apply(
            authored,
            "batch",
            commands=[
                {"op": "set_view", "view": {"contours": 30}},
                {"op": "retime_keyframes", "targets": [target], "delta": 1.5},
            ],
        )
    assert authored.snapshot() == snapshot and authored._storage.read_bytes() == disk

    def fail(candidate):
        raise SceneError("persistence_error", "Cannot save", status=500)

    monkeypatch.setattr(authored, "_persist", fail)
    with pytest.raises(SceneError, match="Cannot save"):
        apply(
            authored,
            "retime_keyframes",
            targets=[{"id": target["id"], "times": [4.5, 7.5]}],
            delta=0.5,
        )
    assert authored.snapshot() == snapshot and authored._storage.read_bytes() == disk


def test_zero_shift_is_normal_protocol_transaction_and_hidden_track_stays_hidden(
    authored,
):
    obj = authored.snapshot()["objects"][0]
    apply(authored, "set_style", id=obj["id"], style={"visible": False})
    before = authored.snapshot()
    after = apply(
        authored,
        "retime_keyframes",
        targets=[{"id": obj["id"], "times": [3, 6]}],
        delta=0,
    )["scene"]
    assert (
        after["objects"] == before["objects"]
        and after["revision"] == before["revision"] + 1
    )


def test_float_destination_collapse_rejects_instead_of_dropping_a_pose(authored):
    recipe = authored.recipe()
    obj = recipe["objects"][0]
    obj["keyframes"] = obj["keyframes"][:2]
    obj["keyframes"][0]["time"] = 0
    obj["keyframes"][1]["time"] = 1e-323
    apply(authored, "load_recipe", recipe=recipe)
    before = authored.snapshot()
    with pytest.raises(SceneError) as error:
        apply(
            authored,
            "retime_keyframes",
            targets=[{"id": obj["id"], "times": [0, 1e-323]}],
            delta=12,
        )
    assert error.value.code == "keyframe_collision" and authored.snapshot() == before


def test_blend_ids_and_static_tracks_are_rejected_without_reference_changes():
    service = SceneService()
    recipe = json.loads((ROOT / "examples/tidal_atlas_confluence.json").read_text())
    apply(service, "load_recipe", recipe=recipe)
    before = service.snapshot()
    for target, code in [
        (before["blends"][0]["id"], "object_not_found"),
        (before["objects"][0]["id"], "keyframe_not_found"),
        ("missing", "object_not_found"),
    ]:
        with pytest.raises(SceneError) as error:
            apply(
                service,
                "retime_keyframes",
                targets=[{"id": target, "times": [0]}],
                delta=1,
            )
        assert error.value.code == code and service.snapshot() == before


def test_http_schemas_and_transaction_match_the_same_shared_service(authored):
    with TestClient(
        create_app(authored, enable_mcp=False), base_url="http://localhost"
    ) as client:
        catalog = client.get("/api/tools").json()
        assert len(catalog) == 22 and any(
            t["name"] == "retime_keyframes" for t in catalog
        )
        before = authored.snapshot()
        args = {
            "targets": [{"id": before["objects"][0]["id"], "times": [3, 6]}],
            "delta": 1,
            "expected_revision": before["revision"],
        }
        result = client.post("/api/tools/retime_keyframes", json=args)
        assert (
            result.status_code == 200
            and result.json()["scene"] == client.get("/api/scene").json()
        )


def test_python_javascript_retime_parity_and_invalid_preview_rejection(authored):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for retiming parity")
    scene = authored.snapshot()
    targets = [{"id": o["id"], "times": [3, 6]} for o in scene["objects"][:2]]
    cases = [
        {"targets": targets, "delta": delta} for delta in [-0.5, 0.25, 1.5, 4, 0]
    ] + [
        {"targets": targets, "delta": 3},
        {"targets": [{"id": scene["objects"][0]["id"], "times": [11]}], "delta": 2},
    ]
    script = "import fs from 'node:fs';import {retimedIslands} from './studio/static/retiming.js';const {scene,cases}=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(cases.map(c=>{try{return retimedIslands(scene,c.targets,c.delta)}catch{return null}})));"
    outputs = json.loads(
        subprocess.run(
            [node, "--input-type=module", "-e", script],
            input=json.dumps({"scene": scene, "cases": cases}),
            text=True,
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
    )
    for case, actual in zip(cases, outputs):
        try:
            expected = retimed_islands(scene, case["targets"], case["delta"])
        except ValueError:
            assert actual is None
        else:
            assert actual == expected
