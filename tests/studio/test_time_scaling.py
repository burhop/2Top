import json
from pathlib import Path
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from geometry.choreography import POSE_FIELDS
from studio.app import create_app
from studio.retiming import scaled_islands, scaled_time
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
    apply(service, "load_recipe", recipe=recipe)
    return service


@pytest.mark.parametrize(
    "anchor,factor,expected",
    [(3, 0.5, [3, 4.5]), (6, 0.5, [4.5, 6]), (4, 2, [2, 8]), (0, 0.5, [1.5, 3])],
)
def test_compression_stretch_and_anchor_preserve_all_geometry_and_easing(
    authored, anchor, factor, expected
):
    before = authored.snapshot()
    obj = before["objects"][0]
    after = apply(
        authored,
        "scale_keyframes",
        targets=[{"id": obj["id"], "times": [6, 3]}],
        anchor=anchor,
        factor=factor,
    )["scene"]
    changed = after["objects"][0]
    for time, destination in zip([3, 6], expected):
        key = next(k for k in obj["keyframes"] if k["time"] == time)
        assert next(k for k in changed["keyframes"] if k["time"] == destination) == {
            **key,
            "time": destination,
        }
    assert (
        changed["parameters"] == obj["parameters"] and changed["style"] == obj["style"]
    )
    assert changed["keyframes"] == sorted(changed["keyframes"], key=lambda k: k["time"])
    assert expected[1] - expected[0] == pytest.approx(3 * factor)
    for field in ["animation", "selection", "view", "blends", "layer_order", "title"]:
        assert after[field] == before[field]
    assert after["objects"][1:] == before["objects"][1:]


def test_selected_times_vacate_together_across_tracks_and_order_is_irrelevant(authored):
    before = authored.snapshot()
    targets = [{"id": o["id"], "times": [9, 3, 6]} for o in before["objects"][:2]]
    expected = scaled_islands(before, targets, 3, 0.5)
    reversed_result = scaled_islands(before, list(reversed(targets)), 3, 0.5)
    assert {o["id"]: o for o in expected} == {o["id"]: o for o in reversed_result}
    after = apply(authored, "scale_keyframes", targets=targets, anchor=3, factor=0.5)[
        "scene"
    ]
    assert after["revision"] == before["revision"] + 1
    assert [k["time"] for k in after["objects"][0]["keyframes"]] == [0, 3, 4.5, 6, 12]


@pytest.mark.parametrize(
    "args",
    [
        {"factor": 0},
        {"factor": -0.5},
        {"factor": 0.0999},
        {"factor": 4.001},
        {"factor": True},
        {"factor": "0.5"},
        {"factor": None},
        {"factor": float("nan")},
        {"factor": float("inf")},
        {"anchor": -0.01},
        {"anchor": 12.01},
        {"anchor": True},
        {"anchor": "3"},
        {"anchor": None},
        {"anchor": float("inf")},
        {"targets": []},
        {"targets": [{"id": "island_ember", "times": [3, 3]}]},
        {"targets": [{"id": "island_ember", "times": [3]}] * 2},
        {"targets": [{"id": f"island_{i}", "times": [3]} for i in range(17)]},
        {"extra": "forbidden"},
    ],
)
def test_invalid_scaling_args_preserve_disk_history_revision_and_retry_key(
    authored, args
):
    before = authored.snapshot()
    disk = authored._storage.read_bytes()
    valid = {
        "op": "scale_keyframes",
        "targets": [{"id": before["objects"][0]["id"], "times": [3, 6]}],
        "anchor": 3,
        "factor": 0.5,
        "expected_revision": before["revision"],
        "request_id": "invalid-scale",
    }
    with pytest.raises(SceneError) as error:
        authored.execute({**valid, **args})
    assert error.value.code == "validation_error"
    assert authored.snapshot() == before and authored._storage.read_bytes() == disk
    assert authored.execute(valid)["ok"]


@pytest.mark.parametrize(
    "times,anchor,factor,code",
    [
        ([3, 6], 3, 2, "keyframe_collision"),
        ([3, 6], 0, 3, "keyframe_range"),
        ([3, 6], 12, 2, "keyframe_range"),
        ([0, 12], 6, 2, "keyframe_range"),
        ([2], 3, 0.5, "keyframe_not_found"),
    ],
)
def test_one_invalid_track_rejects_all_scaling_targets(
    authored, times, anchor, factor, code
):
    before = authored.snapshot()
    disk = authored._storage.read_bytes()
    # A key exactly on the anchor is a legal unchanged first target.
    first = before["objects"][0]
    if anchor not in [k["time"] for k in first["keyframes"]]:
        apply(
            authored,
            "set_keyframe",
            id=first["id"],
            keyframe={
                "time": anchor,
                "parameters": {name: first["parameters"][name] for name in POSE_FIELDS},
                "easing": "smooth",
            },
        )
        before = authored.snapshot()
        disk = authored._storage.read_bytes()
    targets = [
        {"id": first["id"], "times": [anchor]},
        {"id": before["objects"][1]["id"], "times": times},
    ]
    with pytest.raises(SceneError) as error:
        apply(
            authored, "scale_keyframes", targets=targets, anchor=anchor, factor=factor
        )
    assert (
        error.value.code == code
        and authored.snapshot() == before
        and authored._storage.read_bytes() == disk
    )


def test_fractional_identity_and_fixed_anchor_remain_exact_and_collapse_rejects(
    authored,
):
    assert scaled_time(0.1, 10, 1) == 0.1 and scaled_time(0.1, 0.1, 4) == 0.1
    recipe = authored.recipe()
    obj = recipe["objects"][0]
    obj["keyframes"][0]["time"] = 0.1
    apply(authored, "load_recipe", recipe=recipe)
    before = authored.snapshot()
    after = apply(
        authored,
        "scale_keyframes",
        targets=[{"id": obj["id"], "times": [0.1, 3]}],
        anchor=10,
        factor=1,
    )["scene"]
    assert (
        after["objects"] == before["objects"]
        and after["revision"] == before["revision"] + 1
    )
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
            "scale_keyframes",
            targets=[{"id": obj["id"], "times": [0, 1e-323]}],
            anchor=12,
            factor=0.1,
        )
    assert error.value.code == "keyframe_collision" and authored.snapshot() == before


def test_maximum_tracks_and_keys_compress_without_geometry_or_count_changes():
    service = SceneService()
    for i in range(13):
        apply(service, "create_geometry", name=f"Phrase {i}")
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
        {"id": o["id"], "times": [k["time"] for k in o["keyframes"]]}
        for o in recipe["objects"]
    ]
    after = apply(service, "scale_keyframes", targets=targets, anchor=0, factor=0.5)[
        "scene"
    ]
    assert len(after["objects"]) == 16
    assert all(
        [k["time"] for k in o["keyframes"]] == [i / 4 for i in range(24)]
        for o in after["objects"]
    )


@pytest.mark.parametrize("factor", [0.1, 4])
def test_factor_boundaries_and_exact_12_second_destination(authored, factor):
    recipe = authored.recipe()
    obj = recipe["objects"][0]
    obj["keyframes"] = obj["keyframes"][1:3]
    obj["keyframes"][0]["time"] = 9
    obj["keyframes"][1]["time"] = 9.75
    apply(authored, "load_recipe", recipe=recipe)
    after = apply(
        authored,
        "scale_keyframes",
        targets=[{"id": obj["id"], "times": [9, 9.75]}],
        anchor=9,
        factor=factor,
    )["scene"]
    assert [k["time"] for k in after["objects"][0]["keyframes"]] == [
        9,
        9 + 0.75 * factor,
    ]


def test_retry_stale_batch_failure_persistence_and_shared_undo(authored, monkeypatch):
    before = authored.snapshot()
    target = {"id": before["objects"][0]["id"], "times": [3, 6]}
    command = {
        "op": "scale_keyframes",
        "targets": [target],
        "anchor": 3,
        "factor": 0.5,
        "expected_revision": before["revision"],
        "request_id": "scale-once",
    }
    changed = authored.execute(command)
    assert authored.execute(command)["replayed"] is True
    assert SceneService(authored._storage).recipe() == authored.recipe()
    apply(authored, "undo")
    assert authored.recipe()["objects"] == before["objects"]
    apply(authored, "redo")
    assert authored.recipe()["objects"] == changed["scene"]["objects"]
    snapshot = authored.snapshot()
    disk = authored._storage.read_bytes()
    with pytest.raises(SceneError) as error:
        authored.execute({**command, "request_id": "stale-scale"})
    assert error.value.code == "revision_conflict"
    with pytest.raises(SceneError):
        apply(
            authored,
            "batch",
            commands=[
                {"op": "set_view", "view": {"contours": 30}},
                {
                    "op": "scale_keyframes",
                    "targets": [target],
                    "anchor": 3,
                    "factor": 0.5,
                },
            ],
        )
    assert authored.snapshot() == snapshot and authored._storage.read_bytes() == disk

    def fail(candidate):
        raise SceneError("persistence_error", "Cannot save", status=500)

    monkeypatch.setattr(authored, "_persist", fail)
    with pytest.raises(SceneError, match="Cannot save"):
        apply(
            authored,
            "scale_keyframes",
            targets=[{"id": target["id"], "times": [3, 4.5]}],
            anchor=3,
            factor=0.5,
        )
    assert authored.snapshot() == snapshot and authored._storage.read_bytes() == disk


def test_hidden_track_and_playback_are_preserved_by_direct_protocol(authored):
    obj = authored.snapshot()["objects"][0]
    apply(authored, "set_style", id=obj["id"], style={"visible": False})
    apply(authored, "set_view", view={}, animation={"playing": True, "time": 4})
    after = apply(
        authored,
        "scale_keyframes",
        targets=[{"id": obj["id"], "times": [3, 6]}],
        anchor=3,
        factor=0.5,
    )["scene"]
    assert (
        after["animation"]["playing"] is True
        and after["objects"][0]["style"]["visible"] is False
    )


def test_http_catalog_named_command_and_missing_track_are_shared(authored):
    with TestClient(
        create_app(authored, enable_mcp=False), base_url="http://localhost"
    ) as client:
        assert len(client.get("/api/tools").json()) == 23
        before = authored.snapshot()
        args = {
            "targets": [{"id": before["objects"][0]["id"], "times": [3, 6]}],
            "anchor": 3,
            "factor": 0.5,
            "expected_revision": before["revision"],
        }
        result = client.post("/api/tools/scale_keyframes", json=args)
        assert (
            result.status_code == 200
            and result.json()["scene"] == client.get("/api/scene").json()
        )
        snapshot = authored.snapshot()
        missing = client.post(
            "/api/tools/scale_keyframes",
            json={
                **args,
                "targets": [{"id": "missing", "times": [3]}],
                "expected_revision": snapshot["revision"],
            },
        )
        assert missing.status_code == 404 and authored.snapshot() == snapshot


def test_python_javascript_anchor_scaling_and_rejection_parity(authored):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for timing parity")
    scene = authored.snapshot()
    targets = [{"id": o["id"], "times": [3, 6]} for o in scene["objects"][:2]]
    cases = [
        {"targets": targets, "anchor": anchor, "factor": factor}
        for anchor in [0, 3, 4, 6, 12]
        for factor in [0.1, 0.5, 1, 1.5, 2, 4]
    ]
    script = "import fs from 'node:fs';import {scaledIslands,scaledTime} from './studio/static/retiming.js';const {scene,cases}=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify({identity:scaledTime(.1,10,1),anchor:scaledTime(.1,.1,4),results:cases.map(c=>{try{return scaledIslands(scene,c.targets,c.anchor,c.factor)}catch{return null}})}));"
    output = json.loads(
        subprocess.run(
            [node, "--input-type=module", "-e", script],
            input=json.dumps({"scene": scene, "cases": cases}),
            text=True,
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
    )
    assert output["identity"] == 0.1 and output["anchor"] == 0.1
    for case, actual in zip(cases, output["results"]):
        try:
            expected = scaled_islands(
                scene, case["targets"], case["anchor"], case["factor"]
            )
        except ValueError:
            assert actual is None
        else:
            assert actual == expected
