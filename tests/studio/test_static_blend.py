"""Legacy engine composition, deterministic contour parity and scene contracts."""

import copy
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest

from geometry import BaseField, RFunctionCurve
from geometry.kinetic import contour_levels
from geometry.static_blend import StaticBlendField, sample_field_contours
from studio.service import Recipe, SceneError, SceneService

ROOT = Path(__file__).resolve().parents[2]
DEMO = json.loads((ROOT / "examples/tidal_atlas_confluence.json").read_text())


def apply(service, op, **args):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **args}
    )


def node(code, data):
    result = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        input=json.dumps(data),
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "operation,amount",
    [
        ("union", 0),
        ("union", 1),
        ("smooth_union", 0),
        ("smooth_union", 0.45),
        ("smooth_union", 1),
    ],
)
def test_engine_values_contours_and_javascript_parity(operation, amount):
    first, second = [obj["parameters"] for obj in DEMO["objects"]]
    field = StaticBlendField(first, second, operation, amount)
    assert isinstance(field, BaseField) and isinstance(field.curve, RFunctionCurve)
    assert StaticBlendField.from_dict(field.to_dict()).to_dict() == field.to_dict()
    points = [[0, 0], [300, 350], [500, 350], [700, 350], [1200, 900]]
    python = [float(field.evaluate(x, y)) for x, y in points]
    code = "import {createBlend,blendContours} from './studio/static/static-blend.js';let s='';for await(const x of process.stdin)s+=x;const c=JSON.parse(s),f=createBlend(c.first,c.second,c.operation,c.amount);console.log(JSON.stringify({bounds:f.bounds,values:c.points.map(p=>f.evaluate(...p)),layers:blendContours(c.first,c.second,c.operation,c.amount,4,32)}));"
    js = node(
        code,
        {
            "first": first,
            "second": second,
            "operation": operation,
            "amount": amount,
            "points": points,
        },
    )
    assert python == pytest.approx(js["values"], abs=1e-12)
    assert field.bounds() == pytest.approx(js["bounds"])
    layers = sample_field_contours(
        field, field.bounds(), (contour_levels(4) - 1).tolist(), 32
    )
    for layer, mirror in zip(layers, js["layers"]):
        assert layer["level"] == pytest.approx(mirror["level"])
        assert layer["omitted"] == mirror["omitted"] == 0
        assert len(layer["paths"]) == len(mirror["paths"])
        for a, b in zip(layer["paths"], mirror["paths"]):
            np.testing.assert_allclose(a, b, atol=1e-9)
            assert a[0] == a[-1]
    gradient = field.gradient(np.array([350.0, 500.0]), np.array([350.0, 350.0]))
    assert np.isfinite(gradient).all()


def test_demo_merges_two_outer_contours_and_bounds_are_conservative():
    first, second = [obj["parameters"] for obj in DEMO["objects"]]
    union = StaticBlendField(first, second, "union", 0)
    smooth = StaticBlendField(first, second, "smooth_union", 0.85)
    sharp_paths = sample_field_contours(union, union.bounds(), [0], 96)[0]["paths"]
    smooth_paths = sample_field_contours(smooth, smooth.bounds(), [0], 96)[0]["paths"]
    assert len(sharp_paths) == 2 and len(smooth_paths) == 1
    assert union.evaluate(500, 350) > 0 and smooth.evaluate(500, 350) < 0
    for field in (union, smooth):
        xmin, xmax, ymin, ymax = field.bounds()
        xs, ys = np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100)
        assert all(
            np.all(values > 0)
            for values in [
                field.evaluate(xs, ymin),
                field.evaluate(xs, ymax),
                field.evaluate(xmin, ys),
                field.evaluate(xmax, ys),
            ]
        )
    mirrored_demo = node(
        "import {blendDemoRecipe} from './studio/static/blend-demo.js';console.log(JSON.stringify(blendDemoRecipe));",
        {},
    )
    assert mirrored_demo == DEMO
    assert Recipe.model_validate(DEMO).model_dump() == {
        **DEMO,
        "schema_version": 4,
        "layer_order": [o["id"] for o in DEMO["objects"]]
        + [b["id"] for b in DEMO["blends"]],
    }


def test_sampling_omits_open_degenerate_fragments_and_enforces_budgets():
    class Plane:
        def evaluate(self, x, y):
            return x

    result = sample_field_contours(Plane(), [-1, 1, -1, 1], [0], 24)[0]
    assert result["paths"] == [] and result["omitted"] > 0
    for resolution in [0, 193, True]:
        with pytest.raises(ValueError):
            sample_field_contours(Plane(), [-1, 1, -1, 1], [0], resolution)
    with pytest.raises(ValueError):
        sample_field_contours(Plane(), [-1, 1, -1, 1], [0] * 17, 24)


def test_shared_blend_edits_sources_undo_persistence_and_safe_removal(tmp_path):
    service = SceneService(tmp_path / "scene.json")
    before = service.recipe()
    args = {"source_a": "island_ember", "source_b": "island_lagoon", "amount": 0.7}
    result = apply(service, "create_blend", **args)
    blend = result["scene"]["blends"][0]
    assert service.recipe()["objects"] == before["objects"]
    detached = service.get_geometry(blend["id"])
    old_value = float(detached.evaluate(500, 350))
    apply(service, "update_geometry", id="island_ember", parameters={"x": 250})
    assert service.get_geometry(blend["id"]).evaluate(500, 350) != old_value
    assert detached.evaluate(500, 350) == old_value
    apply(
        service,
        "update_blend",
        id=blend["id"],
        operation="union",
        style={"palette": "mono"},
    )
    saved = service.recipe()
    assert SceneService(service._storage).recipe() == saved
    apply(service, "undo")
    assert service.recipe()["blends"][0]["operation"] == "smooth_union"
    apply(service, "redo")
    assert service.recipe() == saved
    with pytest.raises(SceneError, match="Remove"):
        apply(service, "delete_geometry", id="island_ember")
    apply(service, "delete_blend", id=blend["id"])
    assert (
        service.recipe()["blends"] == []
        and service.recipe()["objects"] == saved["objects"]
    )
    apply(service, "undo")
    assert service.recipe() == saved


@pytest.mark.parametrize(
    "patch",
    [
        {"source_a": "unknown"},
        {"source_b": "island_ember"},
        {"amount": -0.01},
        {"amount": 1.01},
        {"amount": float("nan")},
        {"amount": True},
        {"operation": "distance_offset"},
        {"amount": None},
    ],
)
def test_invalid_blend_commands_are_atomic(patch):
    service = SceneService()
    before = service.snapshot()
    with pytest.raises(SceneError):
        apply(
            service,
            "create_blend",
            **{"source_a": "island_ember", "source_b": "island_lagoon", **patch},
        )
    assert service.snapshot() == before


def test_static_reference_cycles_missing_ids_batches_and_legacy_migration(tmp_path):
    service = SceneService(tmp_path / "scene.json")
    apply(service, "load_recipe", recipe=DEMO)
    before = service.snapshot()
    for sources in [
        {"source_a": "blend_confluence"},
        {"source_a": "blend_confluence", "source_b": "blend_confluence"},
    ]:
        with pytest.raises(SceneError):
            apply(service, "update_blend", id="blend_confluence", **sources)
        assert service.snapshot() == before
    pose = {
        k: before["objects"][0]["parameters"][k]
        for k in ["x", "y", "radius", "elongation", "rotation", "warp"]
    }
    with pytest.raises(SceneError, match="static"):
        apply(
            service,
            "batch",
            commands=[
                {"op": "update_blend", "id": "blend_confluence", "amount": 0.2},
                {
                    "op": "set_keyframe",
                    "id": "island_ember",
                    "keyframe": {"time": 0, "parameters": pose},
                },
            ],
        )
    assert service.snapshot() == before
    for filename in ["tidal_atlas_recipe.json", "tidal_atlas_choreography.json"]:
        old = json.loads((ROOT / "examples" / filename).read_text())
        frozen = copy.deepcopy(old)
        migrated = Recipe.model_validate(old).model_dump()
        assert (
            old == frozen
            and migrated["schema_version"] == 4
            and migrated["blends"] == []
        )
        if old["schema_version"] == 2:
            assert migrated["objects"] == old["objects"]
        saved = {**old, "document_id": "legacy_blend", "revision": 9}
        service._storage.write_text(json.dumps(saved))
        assert SceneService(service._storage).recipe() == migrated


def test_blend_budget_namespace_and_safe_dependency_batch():
    service = SceneService()
    for _ in range(2):
        apply(
            service, "create_blend", source_a="island_ember", source_b="island_lagoon"
        )
    before = service.snapshot()
    with pytest.raises(SceneError, match="at most two"):
        apply(
            service, "create_blend", source_a="island_ember", source_b="island_lagoon"
        )
    assert service.snapshot() == before
    invalid = service.recipe()
    invalid["blends"][0]["id"] = "island_ember"
    with pytest.raises(SceneError):
        apply(service, "load_recipe", recipe=invalid)
    assert service.snapshot() == before
    commands = [{"op": "delete_blend", "id": blend["id"]} for blend in before["blends"]]
    commands.append({"op": "delete_geometry", "id": "island_ember"})
    apply(service, "batch", commands=commands)
    assert service.recipe()["blends"] == []
    assert not any(obj["id"] == "island_ember" for obj in service.recipe()["objects"])
    apply(service, "undo")
    assert service.recipe()["blends"] == before["blends"]


def test_blended_geometry_uses_existing_scene_manager_and_graphics_backend():
    service = SceneService()
    apply(service, "load_recipe", recipe=DEMO)
    manager = service.geometry_scene(9)
    assert manager.list_objects() == ["blend_confluence"]
    curve = manager.get_object("blend_confluence")
    assert isinstance(curve, RFunctionCurve) and np.isfinite(curve.bounding_box()).all()
    paths = service.geometry_paths(resolution=64, time_value=9)["paths"][
        "blend_confluence"
    ]
    assert paths["paths"] and paths["closed"]
    apply(service, "update_blend", id="blend_confluence", style={"visible": False})
    assert set(service.geometry_scene(0).list_objects()) == {
        "island_ember",
        "island_lagoon",
    }
