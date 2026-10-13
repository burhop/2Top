"""Center layout contracts: deterministic placement, whole paths and rollback."""

import copy
import json
from pathlib import Path
import random
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from geometry.choreography import sample_parameters
from studio.app import create_app
from studio.layout import laid_out_islands, layout_plan
from studio.service import SceneError, SceneService

ROOT = Path(__file__).resolve().parents[2]


def apply(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


def seed(service, motion=False):
    if motion:
        recipe = json.loads(
            (ROOT / "examples/tidal_atlas_choreography.json").read_text()
        )
        apply(service, "load_recipe", recipe=recipe)
    else:
        for index, island in enumerate(service.snapshot()["objects"]):
            apply(
                service,
                "update_geometry",
                id=island["id"],
                parameters={"x": [230, 390, 790][index], "y": [280, 460, 330][index]},
            )
    return service.snapshot()


@pytest.mark.parametrize("mode", ["align_x", "align_y", "space_x", "space_y"])
def test_layout_anchors_and_orthogonal_coordinates_are_correct(mode):
    service = SceneService()
    before = seed(service)
    ids = [island["id"] for island in before["objects"]]
    after = apply(service, "layout_islands", ids=ids, mode=mode)["scene"]
    axis = mode[-1]
    other = "y" if axis == "x" else "x"
    old = {obj["id"]: obj for obj in before["objects"]}
    if mode.startswith("align"):
        expected = sum(obj["parameters"][axis] for obj in before["objects"]) / 3
        assert [obj["parameters"][axis] for obj in after["objects"]] == pytest.approx(
            [expected] * 3
        )
    else:
        ordered = sorted(before["objects"], key=lambda obj: obj["parameters"][axis])
        low, high = ordered[0]["parameters"][axis], ordered[-1]["parameters"][axis]
        new = {obj["id"]: obj for obj in after["objects"]}
        assert [new[obj["id"]]["parameters"][axis] for obj in ordered] == pytest.approx(
            [low, (low + high) / 2, high]
        )
    for obj in after["objects"]:
        assert obj["parameters"][other] == old[obj["id"]]["parameters"][other]
        for field in ["radius", "elongation", "rotation", "warp", "phase", "lobes"]:
            assert obj["parameters"][field] == old[obj["id"]]["parameters"][field]
        assert obj["style"] == old[obj["id"]]["style"]


@pytest.mark.parametrize("mode", ["align_x", "align_y", "space_x", "space_y"])
def test_complete_paths_follow_anchor_translation_and_persist_undo_redo(tmp_path, mode):
    service = SceneService(tmp_path / "scene.json")
    before = seed(service, motion=True)
    ids = [island["id"] for island in before["objects"]]
    apply(service, "select", ids=ids)
    before = service.snapshot()
    time = 4.5
    plan = {move["id"]: move for move in layout_plan(before, ids, mode, time)}
    after = apply(service, "layout_islands", ids=ids, mode=mode, time=time)["scene"]
    assert after["revision"] == before["revision"] + 1
    for field in ["selection", "layer_order", "blends", "animation", "view"]:
        assert after[field] == before[field]
    for old, new in zip(before["objects"], after["objects"]):
        move = plan[old["id"]]
        assert [(key["time"], key["easing"]) for key in new["keyframes"]] == [
            (key["time"], key["easing"]) for key in old["keyframes"]
        ]
        for moment in [0, 1.5, 4.5, 8.5, 12]:
            a = sample_parameters(old["parameters"], old["keyframes"], moment)
            b = sample_parameters(new["parameters"], new["keyframes"], moment)
            assert b["x"] == pytest.approx(a["x"] + move["dx"])
            assert b["y"] == pytest.approx(a["y"] + move["dy"])
            for field in ["radius", "elongation", "rotation", "warp", "phase", "lobes"]:
                assert b[field] == a[field]
    assert (
        SceneService(tmp_path / "scene.json").snapshot()["objects"] == after["objects"]
    )
    assert apply(service, "undo")["scene"]["objects"] == before["objects"]
    assert apply(service, "redo")["scene"]["objects"] == after["objects"]


@pytest.mark.parametrize(
    "args",
    [
        {"ids": []},
        {"ids": ["island_ember"]},
        {"ids": ["island_ember", "island_ember"]},
        {"ids": ["island_ember", "missing"]},
        {"ids": ["island_ember", "island_lagoon"], "mode": "space_x"},
        {"ids": ["island_ember", "island_lagoon"], "mode": "arbitrary"},
        {"ids": ["island_ember", "island_lagoon"], "time": -1},
        {"ids": ["island_ember", "island_lagoon"], "time": 13},
        {"ids": ["island_ember", "island_lagoon"], "time": True},
        {"ids": ["island_ember", "island_lagoon"], "time": float("nan")},
        {"ids": ["island_ember", "island_lagoon"], "time": "3"},
        {"ids": ["island_ember", "island_lagoon"], "expression": "anything"},
    ],
)
def test_invalid_layout_preserves_disk_redo_revision_and_retry_state(tmp_path, args):
    path = tmp_path / "scene.json"
    service = SceneService(path)
    seed(service)
    apply(service, "set_style", id="island_ember", style={"opacity": 0.8})
    apply(service, "undo")
    before, disk = service.snapshot(), path.read_bytes()
    requests = copy.deepcopy(service._requests)
    with pytest.raises(SceneError):
        apply(
            service,
            "layout_islands",
            request_id="layout-attempt",
            **{"mode": "align_x", **args},
        )
    assert (
        service.snapshot() == before
        and path.read_bytes() == disk
        and service._requests == requests
    )
    good = apply(
        service,
        "layout_islands",
        ids=["island_ember", "island_lagoon"],
        mode="align_y",
        request_id="layout-attempt",
    )
    assert good["scene"]["revision"] == before["revision"] + 1


def test_blend_ids_reject_but_retained_source_links_remain_valid():
    service = SceneService()
    seed(service)
    blend = apply(
        service, "create_blend", source_a="island_ember", source_b="island_lagoon"
    )["scene"]["blends"][0]["id"]
    before = service.snapshot()
    with pytest.raises(SceneError, match="islands only"):
        apply(service, "layout_islands", ids=["island_ember", blend], mode="align_x")
    assert service.snapshot() == before
    after = apply(
        service, "layout_islands", ids=["island_ember", "island_lagoon"], mode="align_y"
    )["scene"]
    assert (
        after["blends"] == before["blends"]
        and after["objects"][2] == before["objects"][2]
    )


def test_ties_reversed_selection_and_coincident_centers_are_deterministic():
    service = SceneService()
    before = seed(service)
    apply(service, "update_geometry", id="island_lagoon", parameters={"x": 230})
    before = service.snapshot()
    ids = [obj["id"] for obj in before["objects"]]
    plan = layout_plan(before, ids, "space_x")
    assert plan == layout_plan(before, list(reversed(ids)), "space_x")
    assert plan[0]["id"] == "island_ember" and plan[0]["dx"] == 0
    assert next(move for move in plan if move["id"] == "island_lagoon")["dx"] == 280
    for obj in before["objects"]:
        apply(service, "update_geometry", id=obj["id"], parameters={"x": 400})
    same = service.snapshot()
    assert laid_out_islands(same, ids, "space_x") == sorted(
        same["objects"], key=lambda obj: obj["id"]
    )
    result = apply(service, "layout_islands", ids=ids, mode="space_x")["scene"]
    assert result["objects"] == same["objects"]
    assert result["history"]["entries"][-1]["changes"]["updated_ids"] == []


def test_hidden_islands_two_island_alignment_and_maximum_selection():
    service = SceneService()
    seed(service)
    apply(service, "set_style", id="island_lagoon", style={"visible": False})
    before = service.snapshot()
    after = apply(
        service, "layout_islands", ids=["island_ember", "island_lagoon"], mode="align_x"
    )["scene"]
    assert (
        after["objects"][1]["style"]["visible"] is False
        and after["objects"][2] == before["objects"][2]
    )
    for index in range(13):
        apply(
            service,
            "create_geometry",
            parameters={"x": 300 + index * 40, "y": 300},
            name=f"Extra {index}",
        )
    snapshot = service.snapshot()
    ids = [obj["id"] for obj in snapshot["objects"]]
    assert (
        len(apply(service, "layout_islands", ids=ids, mode="space_x")["affected_ids"])
        == 16
    )


def test_fractional_coincident_centers_remain_exactly_unchanged():
    service = SceneService()
    ids = [island["id"] for island in service.snapshot()["objects"]]
    for key in ids:
        apply(service, "update_geometry", id=key, parameters={"x": 0.1})
    before = service.snapshot()
    assert all(move["dx"] == 0 for move in layout_plan(before, ids, "align_x"))
    assert (
        apply(service, "layout_islands", ids=ids, mode="align_x")["scene"]["objects"]
        == before["objects"]
    )


def test_any_out_of_bounds_key_or_persistence_failure_rolls_back_every_island(
    tmp_path, monkeypatch
):
    path = tmp_path / "scene.json"
    service = SceneService(path)
    before = seed(service, motion=True)
    ids = [obj["id"] for obj in before["objects"]]
    # Endpoint keys are legal individually, but a base-center move can push one out.
    island = before["objects"][0]
    key = copy.deepcopy(island["keyframes"][0])
    key["parameters"]["x"] = 1999
    apply(service, "set_keyframe", id=island["id"], keyframe=key)
    before = service.snapshot()
    disk = path.read_bytes()
    with pytest.raises(SceneError, match="exceeds x"):
        apply(service, "layout_islands", ids=ids, mode="align_x", time=12)
    assert service.snapshot() == before and path.read_bytes() == disk

    def failed(_candidate):
        raise SceneError("persistence_error", "Cannot save scene", status=500)

    monkeypatch.setattr(service, "_persist", failed)
    with pytest.raises(SceneError, match="Cannot save"):
        apply(service, "layout_islands", ids=ids, mode="align_y", time=12)
    assert service.snapshot() == before and path.read_bytes() == disk


def test_replay_conflicts_and_batch_rollback_use_existing_transaction_contract():
    service = SceneService()
    seed(service)
    before = service.snapshot()
    ids = [obj["id"] for obj in before["objects"]]
    args = {
        "op": "layout_islands",
        "ids": ids,
        "mode": "space_x",
        "expected_revision": before["revision"],
        "request_id": "space-once",
    }
    after = service.execute(args)
    replayed = service.execute(args)
    assert replayed["replayed"] and replayed["scene"] == after["scene"]
    with pytest.raises(SceneError) as error:
        service.execute({**args, "mode": "align_y"})
    assert error.value.code == "request_id_reused"
    with pytest.raises(SceneError) as error:
        service.execute({**args, "request_id": "stale"})
    assert error.value.code == "revision_conflict"
    before = service.snapshot()
    with pytest.raises(SceneError):
        apply(
            service,
            "batch",
            commands=[
                {"op": "layout_islands", "ids": ids, "mode": "align_y"},
                {"op": "delete_geometry", "id": "missing"},
            ],
        )
    assert service.snapshot() == before


def test_http_layout_returns_structured_errors_without_partial_state():
    service = SceneService()
    seed(service)
    before = service.snapshot()
    ids = [obj["id"] for obj in before["objects"]]
    with TestClient(
        create_app(service, enable_mcp=False), base_url="http://localhost"
    ) as client:
        response = client.post(
            "/api/tools/layout_islands",
            json={
                "ids": ids,
                "mode": "align_y",
                "expected_revision": before["revision"],
            },
        )
        assert (
            response.status_code == 200
            and response.json()["scene"] == service.snapshot()
        )
        snapshot = service.snapshot()
        failed = client.post(
            "/api/command",
            json={
                "op": "layout_islands",
                "ids": ids[:2],
                "mode": "space_x",
                "expected_revision": snapshot["revision"],
            },
        )
        assert failed.status_code == 400 and service.snapshot() == snapshot


def test_python_javascript_plans_tracks_and_ties_have_numeric_parity():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for layout parity")
    service = SceneService()
    scene = seed(service, motion=True)
    ids = [obj["id"] for obj in scene["objects"]]
    rng = random.Random(900)
    cases = [
        {
            "scene": scene,
            "ids": ids if index % 2 else list(reversed(ids)),
            "mode": mode,
            "time": rng.uniform(0, 12),
        }
        for index in range(5)
        for mode in ["align_x", "align_y", "space_x", "space_y"]
    ]
    script = "import fs from 'node:fs';import {layoutPlan,laidOutIslands} from './studio/static/layout.js';const cases=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(cases.map(c=>({plan:layoutPlan(c.scene,c.ids,c.mode,c.time),islands:laidOutIslands(c.scene,c.ids,c.mode,c.time)}))));"
    outputs = json.loads(
        subprocess.run(
            [node, "--input-type=module", "-e", script],
            input=json.dumps(cases),
            text=True,
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
    )
    for case, actual in zip(cases, outputs):
        expected = layout_plan(scene, case["ids"], case["mode"], case["time"])
        for a, b in zip(expected, actual["plan"]):
            assert (
                a["id"] == b["id"]
                and a["dx"] == pytest.approx(b["dx"], abs=1e-9)
                and a["dy"] == pytest.approx(b["dy"], abs=1e-9)
            )
        python = laid_out_islands(scene, case["ids"], case["mode"], case["time"])
        for a, b in zip(python, actual["islands"]):
            assert a["id"] == b["id"] and a["parameters"] == pytest.approx(
                b["parameters"], abs=1e-9
            )
            assert a["style"] == b["style"]
            for ka, kb in zip(a["keyframes"], b["keyframes"]):
                assert (
                    ka["time"] == kb["time"]
                    and ka["easing"] == kb["easing"]
                    and ka["parameters"] == pytest.approx(kb["parameters"], abs=1e-9)
                )
