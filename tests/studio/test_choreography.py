"""Authored pose contracts, numeric parity, transactions and legacy migration."""

import copy
import json
import subprocess
from pathlib import Path

import pytest

from geometry.choreography import POSE_FIELDS, sample_parameters
from studio.service import Recipe, SceneError, SceneService

ROOT = Path(__file__).resolve().parents[2]


def pose(**patch):
    return {
        "x": 300,
        "y": 350,
        "radius": 180,
        "elongation": 1,
        "rotation": -30,
        "warp": 0.4,
        **patch,
    }


def key(time, easing="linear", **patch):
    return {"time": time, "parameters": pose(**patch), "easing": easing}


def apply(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


def test_interpolation_endpoints_holds_and_no_mutation():
    parameters = SceneService().recipe()["objects"][0]["parameters"]
    keys = [key(2), key(10, x=700, radius=260, rotation=150, warp=0.8)]
    original = copy.deepcopy(keys)
    assert sample_parameters(parameters, keys, 0)["x"] == 300
    assert sample_parameters(parameters, keys, 12)["x"] == 700
    assert sample_parameters(parameters, keys, 4)["x"] == 400
    keys[0]["easing"] = "smooth"
    assert sample_parameters(parameters, keys, 4)["x"] == 362.5
    assert sample_parameters(parameters, keys, 6)["rotation"] == 60
    assert sample_parameters(parameters, keys, 4)["lobes"] == parameters["lobes"]
    assert original[0] == key(2)
    frozen = copy.deepcopy(keys)
    sample_parameters(parameters, keys, 30)
    assert keys == frozen


def test_empty_single_and_looped_tracks():
    parameters = SceneService().recipe()["objects"][0]["parameters"]
    assert sample_parameters(parameters, [], 8) == parameters
    assert sample_parameters(parameters, [key(5)], 0)["radius"] == 180
    keys = [key(0), key(6, x=700), key(12)]
    assert sample_parameters(parameters, keys, 0) == sample_parameters(
        parameters, keys, 12
    )
    assert sample_parameters(parameters, keys, 3) == sample_parameters(
        parameters, keys, 27
    )


def test_upsert_delete_shared_undo_redo_and_atomic_batch():
    service = SceneService()
    service.invoke(
        "set_keyframe",
        {"id": "island_ember", "keyframe": key(6), "expected_revision": 0},
        actor="mcp",
    )
    service.invoke(
        "set_keyframe",
        {"id": "island_ember", "keyframe": key(0), "expected_revision": 1},
        actor="webmcp",
    )
    apply(service, "set_keyframe", id="island_ember", keyframe=key(6, x=700))
    keys = service.recipe()["objects"][0]["keyframes"]
    assert [k["time"] for k in keys] == [0, 6]
    assert keys[1]["parameters"]["x"] == 700
    apply(service, "undo")
    assert service.recipe()["objects"][0]["keyframes"][1]["parameters"]["x"] == 300
    apply(service, "redo")
    assert service.get_geometry("island_ember", time_value=3).parameters["x"] == 500
    before = service.snapshot()
    with pytest.raises(SceneError):
        apply(
            service,
            "batch",
            commands=[
                {"op": "delete_keyframe", "id": "island_ember", "time": 0},
                {"op": "delete_keyframe", "id": "missing", "time": 0},
            ],
        )
    assert service.snapshot() == before
    apply(service, "delete_keyframe", id="island_ember", time=6)
    assert len(service.recipe()["objects"][0]["keyframes"]) == 1
    apply(service, "undo")
    assert service.recipe()["objects"][0]["keyframes"] == keys


@pytest.mark.parametrize(
    "broken",
    [
        key(-0.1),
        key(12.1),
        key(float("nan")),
        key(0, easing="execute"),
        key(0, x=True),
        key(0, radius=79),
        key(0, warp=float("inf")),
        {"time": 0, "parameters": {"x": 300}},
        {**key(0), "callback": "eval"},
    ],
)
def test_malformed_keys_never_commit(broken):
    service = SceneService()
    before = service.snapshot()
    with pytest.raises(SceneError):
        apply(service, "set_keyframe", id="island_ember", keyframe=broken)
    assert service.snapshot() == before


def test_track_limits_sorting_stale_writes_and_replay():
    service = SceneService()
    for i in range(24):
        apply(service, "set_keyframe", id="island_ember", keyframe=key(i / 2))
    before = service.snapshot()
    with pytest.raises(SceneError, match="at most 24"):
        apply(service, "set_keyframe", id="island_ember", keyframe=key(12))
    assert service.snapshot() == before
    args = {
        "id": "island_ember",
        "keyframe": key(0, x=400),
        "expected_revision": 24,
        "request_id": "key_once",
    }
    first = service.invoke("set_keyframe", args)
    assert (
        service.invoke("set_keyframe", args)["transaction_id"]
        == first["transaction_id"]
    )
    with pytest.raises(SceneError, match="Artwork changed"):
        service.invoke(
            "delete_keyframe",
            {"id": "island_ember", "time": 0, "expected_revision": 24},
        )
    recipe = service.recipe()
    for keys in [[key(6), key(0)], [key(0), key(0)]]:
        recipe["objects"][0]["keyframes"] = keys
        with pytest.raises(SceneError):
            apply(service, "load_recipe", recipe=recipe)


def test_legacy_migration_disk_roundtrip_and_duplicate(tmp_path):
    legacy = json.loads((ROOT / "examples/tidal_atlas_recipe.json").read_text())
    untouched = copy.deepcopy(legacy)
    migrated = Recipe.model_validate(legacy).model_dump()
    assert legacy == untouched and migrated["schema_version"] == 2
    assert all(obj["keyframes"] == [] for obj in migrated["objects"])
    path = tmp_path / "scene.json"
    service = SceneService(path)
    apply(service, "load_recipe", recipe=legacy)
    apply(service, "set_keyframe", id="island_ember", keyframe=key(0))
    apply(service, "set_keyframe", id="island_ember", keyframe=key(12, radius=240))
    assert SceneService(path).recipe() == service.recipe()
    # Existing persisted schema-1 documents also migrate on startup.
    saved = {**legacy, "document_id": "legacy_doc", "revision": 7}
    path.write_text(json.dumps(saved))
    assert SceneService(path).recipe() == migrated
    obj = service.recipe()["objects"][0]
    apply(
        service,
        "create_geometry",
        name="Choreographed copy",
        parameters=obj["parameters"],
        keyframes=obj["keyframes"],
    )
    assert service.recipe()["objects"][-1]["keyframes"] == obj["keyframes"]


def test_python_javascript_parity_and_demo_reproducibility():
    demo = json.loads((ROOT / "examples/tidal_atlas_choreography.json").read_text())
    assert Recipe.model_validate(demo).model_dump() == demo
    demo_result = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            "import {demoRecipe} from './studio/static/demo.js'; console.log(JSON.stringify(demoRecipe));",
        ],
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    assert json.loads(demo_result.stdout) == demo
    cases = [
        {"parameters": obj["parameters"], "keys": obj["keyframes"], "time": t}
        for obj in demo["objects"]
        for t in [0, 0.75, 3, 4.5, 6, 9, 12, 27]
    ]
    code = "import {sampleParameters} from './studio/static/choreography.js'; let s=''; for await (const x of process.stdin) s+=x; console.log(JSON.stringify(JSON.parse(s).map(c=>sampleParameters(c.parameters,c.keys,c.time))));"
    result = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        input=json.dumps(cases),
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    for case, js in zip(cases, json.loads(result.stdout)):
        assert sample_parameters(
            case["parameters"], case["keys"], case["time"]
        ) == pytest.approx(js)
    for obj in demo["objects"]:
        start = sample_parameters(obj["parameters"], obj["keyframes"], 0)
        middle = sample_parameters(obj["parameters"], obj["keyframes"], 6)
        assert start == sample_parameters(obj["parameters"], obj["keyframes"], 12)
        assert any(abs(start[field] - middle[field]) > 1 for field in POSE_FIELDS)
