"""Whole-choreography group transactions, bounds, geometry and browser parity."""

import copy
import json
import math
from pathlib import Path
import random
import shutil
import subprocess

import numpy as np
import pytest
from fastapi.testclient import TestClient

from geometry.choreography import sample_parameters
from geometry.kinetic import generate_contours
from studio.app import create_app
from studio.service import SceneError, SceneService
from studio.transforms import resolve_islands, transformed_islands

ROOT = Path(__file__).resolve().parents[2]


def command(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


def motion(service):
    recipe = json.loads((ROOT / "examples/tidal_atlas_choreography.json").read_text())
    command(service, "load_recipe", recipe=recipe)
    return service.snapshot()


def test_transform_moves_complete_paths_and_preserves_interpolation_and_history(
    tmp_path,
):
    service = SceneService(tmp_path / "scene.json")
    before = motion(service)
    ids = [obj["id"] for obj in before["objects"][:2]]
    command(service, "select", ids=ids)
    before = service.snapshot()
    pivot = {"x": 500, "y": 350}
    options = dict(ids=ids, dx=12, dy=-18, scale=1.1, rotation=20, pivot=pivot)
    after = command(service, "transform_layers", **options)["scene"]
    assert after["revision"] == before["revision"] + 1
    for key in ["selection", "view", "animation", "layer_order", "blends"]:
        assert after[key] == before[key]
    assert after["objects"][2] == before["objects"][2]
    for old, new in zip(before["objects"][:2], after["objects"][:2]):
        assert new["style"] == old["style"]
        assert new["parameters"]["lobes"] == old["parameters"]["lobes"]
        assert [(k["time"], k["easing"]) for k in new["keyframes"]] == [
            (k["time"], k["easing"]) for k in old["keyframes"]
        ]
        # Affine centers/radii and additive authored angles commute with easing.
        angle = math.radians(20)
        matrix = 1.1 * np.array(
            [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
        )
        for time in [0, 1.5, 3, 7.5, 12]:
            a = sample_parameters(old["parameters"], old["keyframes"], time)
            b = sample_parameters(new["parameters"], new["keyframes"], time)
            expected = matrix @ (np.array([a["x"], a["y"]]) - [500, 350]) + [512, 332]
            assert [b["x"], b["y"]] == pytest.approx(expected)
            assert b["radius"] == pytest.approx(a["radius"] * 1.1)
            assert b["rotation"] == pytest.approx(a["rotation"] + 20)
    restarted = SceneService(tmp_path / "scene.json").snapshot()
    assert restarted["objects"] == after["objects"]
    undone = command(service, "undo")["scene"]
    assert undone["objects"] == before["objects"]
    assert undone["selection"] == ids
    assert command(service, "redo")["scene"]["objects"] == after["objects"]


def test_static_geometry_contours_are_exactly_transformed_without_engine_changes():
    service = SceneService()
    island = service.snapshot()["objects"][0]
    p = island["parameters"]
    pivot = {"x": 400, "y": 300}
    transformed = transformed_islands(
        [island], dx=20, dy=10, scale=1.2, rotation=30, pivot=pivot
    )[0]["parameters"]
    old = np.asarray(generate_contours(p, motion=0, count=8, samples=48))
    new = np.asarray(generate_contours(transformed, motion=0, count=8, samples=48))
    angle = math.radians(30)
    matrix = np.array(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
    )
    expected = ((old - [400, 300]) * 1.2) @ matrix.T + [420, 310]
    np.testing.assert_allclose(new, expected, atol=1e-10)


def test_blends_expand_sources_once_even_when_selected_with_shared_sources():
    service = SceneService()
    ids = [obj["id"] for obj in service.snapshot()["objects"]]
    first = command(service, "create_blend", source_a=ids[0], source_b=ids[1])["scene"][
        "blends"
    ][0]["id"]
    second = command(service, "create_blend", source_a=ids[0], source_b=ids[2])[
        "scene"
    ]["blends"][1]["id"]
    command(service, "select", ids=[first, ids[0], second])
    before = service.snapshot()
    result = command(
        service, "transform_layers", ids=before["selection"], dx=25, dy=-10
    )
    assert result["affected_ids"] == ids
    after = result["scene"]
    for old, new in zip(before["objects"], after["objects"]):
        assert new["parameters"]["x"] == old["parameters"]["x"] + 25
        assert new["parameters"]["y"] == old["parameters"]["y"] - 10
    assert after["blends"] == before["blends"]
    assert after["selection"] == before["selection"]
    assert after["layer_order"] == before["layer_order"]


@pytest.mark.parametrize(
    "args",
    [
        {"ids": []},
        {"ids": ["island_ember", "island_ember"]},
        {"ids": ["missing"]},
        {"ids": ["island_ember"], "scale": 0},
        {"ids": ["island_ember"], "scale": -1},
        {"ids": ["island_ember"], "scale": 5},
        {"ids": ["island_ember"], "scale": True},
        {"ids": ["island_ember"], "rotation": 361},
        {"ids": ["island_ember"], "dx": float("nan")},
        {"ids": ["island_ember"], "dy": float("inf")},
        {"ids": ["island_ember"], "pivot": {"x": "500", "y": 350}},
        {"ids": ["island_ember"], "expression": "anything"},
    ],
)
def test_invalid_transform_preserves_disk_history_redo_revision_and_retry_keys(
    tmp_path, args
):
    path = tmp_path / "scene.json"
    service = SceneService(path)
    command(service, "set_style", id="island_ember", style={"opacity": 0.8})
    command(service, "undo")
    before, disk = service.snapshot(), path.read_bytes()
    replay = copy.deepcopy(service._requests)
    with pytest.raises(SceneError):
        command(service, "transform_layers", request_id="failed-transform", **args)
    assert service.snapshot() == before
    assert path.read_bytes() == disk
    assert service._requests == replay
    corrected = command(
        service,
        "transform_layers",
        ids=["island_ember"],
        dx=5,
        request_id="failed-transform",
    )
    assert corrected["scene"]["revision"] == before["revision"] + 1


@pytest.mark.parametrize(
    "field,value,options",
    [
        ("x", 1999, {"dx": 2}),
        ("y", -699, {"dy": -2}),
        ("radius", 399, {"scale": 1.1}),
        ("rotation", 355, {"rotation": 10}),
    ],
)
def test_one_key_exceeding_a_bound_rejects_the_entire_group(field, value, options):
    service = SceneService()
    before = motion(service)
    ids = [obj["id"] for obj in before["objects"][:2]]
    key = copy.deepcopy(before["objects"][1]["keyframes"][0])
    key["parameters"][field] = value
    command(service, "set_keyframe", id=ids[1], keyframe=key)
    before = service.snapshot()
    with pytest.raises(SceneError, match=f"exceeds {field} limits"):
        command(service, "transform_layers", ids=ids, **options)
    assert service.snapshot() == before


def test_transform_stale_conflict_replay_and_atomic_batch():
    service = SceneService()
    before = service.snapshot()
    ids = [obj["id"] for obj in before["objects"][:2]]
    payload = {
        "op": "transform_layers",
        "expected_revision": 0,
        "ids": ids,
        "dx": 10,
        "request_id": "move-pair",
    }
    result = service.execute(payload)
    replayed = service.execute(payload)
    assert replayed["replayed"] is True
    assert replayed["scene"] == result["scene"]
    assert len(service.snapshot()["history"]["entries"]) == 1
    with pytest.raises(SceneError) as error:
        service.execute({**payload, "dx": 11})
    assert error.value.code == "request_id_reused"
    with pytest.raises(SceneError) as error:
        service.execute({**payload, "request_id": "stale"})
    assert error.value.code == "revision_conflict"
    before = service.snapshot()
    with pytest.raises(SceneError):
        command(
            service,
            "batch",
            commands=[
                {"op": "transform_layers", "ids": ids, "dx": 10},
                {"op": "delete_geometry", "id": "missing"},
            ],
        )
    assert service.snapshot() == before
    after = command(
        service,
        "batch",
        commands=[
            {"op": "select", "ids": ids},
            {"op": "transform_layers", "ids": ids, "dy": 5},
        ],
    )["scene"]
    assert after["revision"] == before["revision"] + 1
    assert after["selection"] == ids
    assert command(service, "undo")["scene"]["objects"] == before["objects"]


def test_http_transform_uses_shared_scene_and_structured_errors():
    service = SceneService()
    with TestClient(
        create_app(service, enable_mcp=False), base_url="http://localhost"
    ) as client:
        before = service.snapshot()
        ids = [obj["id"] for obj in before["objects"][:2]]
        ok = client.post(
            "/api/tools/transform_layers",
            json={"ids": ids, "dx": 10, "expected_revision": 0},
        )
        assert ok.status_code == 200
        assert ok.json()["scene"] == service.snapshot()
        snapshot = service.snapshot()
        failed = client.post(
            "/api/command",
            json={
                "op": "transform_layers",
                "ids": ids,
                "scale": 4,
                "expected_revision": snapshot["revision"],
            },
        )
        assert (
            failed.status_code == 400
            and failed.json()["error"]["code"] == "validation_error"
        )
        assert service.snapshot() == snapshot


def test_python_javascript_transform_and_source_resolution_parity():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for browser/Python parity")
    rng = random.Random(800)
    service = SceneService()
    base = motion(service)
    islands = base["objects"][:2]
    cases = [
        {
            "islands": islands,
            "options": {
                "dx": rng.uniform(-30, 30),
                "dy": rng.uniform(-30, 30),
                "scale": rng.uniform(0.9, 1.1),
                "rotation": rng.uniform(-30, 30),
                "pivot": {"x": 500, "y": 350},
            },
        }
        for _ in range(20)
    ]
    script = "import fs from 'node:fs';import {transformedIslands,resolveIslands} from './studio/static/transforms.js';const data=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(data.map(c=>transformedIslands(c.islands,c.options))));"
    actual = json.loads(
        subprocess.run(
            [node, "--input-type=module", "-e", script],
            input=json.dumps(cases),
            text=True,
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
    )
    for case, js in zip(cases, actual):
        python = transformed_islands(case["islands"], **case["options"])
        for a, b in zip(python, js):
            assert a["id"] == b["id"] and a["style"] == b["style"]
            assert a["parameters"] == pytest.approx(b["parameters"], abs=1e-9)
            for ka, kb in zip(a["keyframes"], b["keyframes"]):
                assert ka["time"] == kb["time"] and ka["easing"] == kb["easing"]
                assert ka["parameters"] == pytest.approx(kb["parameters"], abs=1e-9)
    assert base["objects"][:2] == islands  # Pure helpers do not mutate inputs.


def test_shared_sources_and_identity_default_pivot_are_deterministic():
    service = SceneService()
    before = service.snapshot()
    targets = resolve_islands(before, ["island_ember", "island_moon"])
    assert transformed_islands(targets) == targets
    after = command(
        service, "transform_layers", ids=[obj["id"] for obj in targets], scale=1.1
    )["scene"]
    center = np.mean(
        [[obj["parameters"]["x"], obj["parameters"]["y"]] for obj in targets], axis=0
    )
    for old, new in zip(
        targets,
        [obj for obj in after["objects"] if obj["id"] in {o["id"] for o in targets}],
    ):
        assert [new["parameters"]["x"], new["parameters"]["y"]] == pytest.approx(
            center
            + 1.1
            * (np.array([old["parameters"]["x"], old["parameters"]["y"]]) - center)
        )


def test_full_supported_layer_set_transforms_without_a_new_group_record():
    service = SceneService()
    for index in range(13):
        command(service, "create_geometry", name=f"Extra {index}")
    ids = [obj["id"] for obj in service.snapshot()["objects"]]
    command(service, "create_blend", source_a=ids[0], source_b=ids[1])
    command(service, "create_blend", source_a=ids[0], source_b=ids[2])
    before = service.snapshot()
    result = command(service, "transform_layers", ids=before["layer_order"], dx=5)
    assert len(result["affected_ids"]) == 16
    assert len(result["scene"]["layer_order"]) == 18
    assert result["scene"]["schema_version"] == 4
    assert result["scene"]["blends"] == before["blends"]
    for old, new in zip(before["objects"], result["scene"]["objects"]):
        assert new["parameters"]["x"] == old["parameters"]["x"] + 5


def test_shared_source_resolution_and_limit_rejection_match_javascript():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for browser/Python parity")
    service = SceneService()
    first = command(
        service, "create_blend", source_a="island_ember", source_b="island_lagoon"
    )["scene"]["blends"][0]["id"]
    second = command(
        service, "create_blend", source_a="island_ember", source_b="island_moon"
    )["scene"]["blends"][1]["id"]
    scene = service.snapshot()
    ids = [first, "island_ember", second]
    script = "import fs from 'node:fs';import {resolveIslands,transformedIslands} from './studio/static/transforms.js';const {scene,ids}=JSON.parse(fs.readFileSync(0,'utf8'));const islands=resolveIslands(scene,ids);let rejected=false;try{transformedIslands(islands,{scale:4});}catch{rejected=true;}const changed=transformedIslands(islands,{dx:10});changed[0].style.opacity=.1;console.log(JSON.stringify({ids:islands.map(o=>o.id),rejected,originalOpacity:scene.objects[0].style.opacity}));"
    actual = json.loads(
        subprocess.run(
            [node, "--input-type=module", "-e", script],
            input=json.dumps({"scene": scene, "ids": ids}),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    )
    assert actual["ids"] == [island["id"] for island in resolve_islands(scene, ids)]
    assert actual["rejected"] is True
    assert actual["originalOpacity"] == scene["objects"][0]["style"]["opacity"]
    targets = resolve_islands(scene, ids)
    changed = transformed_islands(targets, dx=10)
    changed[0]["style"]["opacity"] = 0.1
    assert targets[0]["style"] == scene["objects"][0]["style"]
