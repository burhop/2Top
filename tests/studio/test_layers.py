"""Order/styles are derived display policy, never geometry or operand mutations."""

import copy
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest

from studio.service import Recipe, SceneError, SceneService

ROOT = Path(__file__).resolve().parents[2]
DEMO = json.loads(
    (ROOT / "examples/tidal_atlas_layers.json").read_text(encoding="utf-8")
)


def apply(service, op, **kwargs):
    return service.execute(
        {"op": op, "expected_revision": service.snapshot()["revision"], **kwargs}
    )


def test_layer_order_style_selection_persistence_and_undo(tmp_path):
    service = SceneService(tmp_path / "layers.json")
    apply(service, "load_recipe", recipe=DEMO)
    before = service.recipe()
    bounds = service.get_geometry("blend_confluence").bounds()
    value = service.get_geometry("blend_confluence").evaluate(np.array([300, 500]), 350)
    order = list(reversed(before["layer_order"]))
    apply(
        service,
        "batch",
        commands=[
            {"op": "reorder_layers", "order": order},
            {
                "op": "set_style",
                "id": "blend_confluence",
                "style": {"palette": "lagoon", "opacity": 0.25},
            },
            {"op": "select", "ids": ["blend_confluence"]},
        ],
    )
    assert service.recipe()["layer_order"] == order
    assert service.invoke("get_selection", {})["objects"][0]["id"] == "blend_confluence"
    assert service.get_geometry("blend_confluence").bounds() == bounds
    np.testing.assert_array_equal(
        service.get_geometry("blend_confluence").evaluate(np.array([300, 500]), 350),
        value,
    )
    manager = service.geometry_scene(0)
    assert manager.list_objects() == [
        "island_glass",
        "blend_confluence",
        "island_lowtide",
    ]
    assert service.recipe()["objects"] == before["objects"]
    assert SceneService(service._storage).recipe() == service.recipe()
    apply(service, "undo")
    assert service.recipe() == before
    apply(service, "redo")
    assert service.recipe()["layer_order"] == order
    saved = json.loads(json.dumps(service.recipe()))
    apply(service, "load_recipe", recipe=saved)
    assert service.recipe() == saved


@pytest.mark.parametrize(
    "kind", ["missing", "duplicate", "unknown", "extra", "null", "nonlist"]
)
def test_invalid_order_is_atomic_with_style_and_disk(tmp_path, kind):
    service = SceneService(tmp_path / "layers.json")
    apply(service, "load_recipe", recipe=DEMO)
    before, disk = service.snapshot(), service._storage.read_bytes()
    ids = before["layer_order"]
    order = {
        "missing": ids[:-1],
        "duplicate": ids[:-1] + [ids[0]],
        "unknown": ids[:-1] + ["missing"],
        "extra": ids + ["missing"],
        "null": None,
        "nonlist": "island_ember",
    }[kind]
    with pytest.raises(SceneError):
        apply(
            service,
            "batch",
            commands=[
                {
                    "op": "set_style",
                    "id": "blend_confluence",
                    "style": {"opacity": 0.2},
                },
                {"op": "reorder_layers", "order": order},
            ],
        )
    assert service.snapshot() == before and service._storage.read_bytes() == disk
    recipe = service.recipe()
    recipe["layer_order"] = order
    with pytest.raises(SceneError):
        apply(service, "load_recipe", recipe=recipe)
    assert service.snapshot() == before


@pytest.mark.parametrize(
    "style",
    [
        {"opacity": 0},
        {"opacity": 1.01},
        {"opacity": float("nan")},
        {"opacity": True},
        {"palette": "invalid"},
        {"visible": None},
    ],
)
def test_style_bounds_reject_without_mutating_sources(style):
    service = SceneService()
    apply(service, "load_recipe", recipe=DEMO)
    before = service.snapshot()
    with pytest.raises(SceneError):
        apply(service, "set_style", id="blend_confluence", style=style)
    assert service.snapshot() == before


def test_hidden_sources_retain_fields_dependencies_and_order():
    service = SceneService()
    apply(service, "load_recipe", recipe=DEMO)
    original = service.recipe()
    apply(service, "set_style", id="island_ember", style={"visible": False})
    assert service.geometry_scene(0).list_objects() == [
        "island_lowtide",
        "blend_confluence",
        "island_glass",
    ]
    before = service.snapshot()
    with pytest.raises(SceneError, match="blends"):
        apply(service, "delete_geometry", id="island_ember")
    assert service.snapshot() == before
    apply(service, "update_geometry", id="island_ember", parameters={"x": 250})
    assert service.get_geometry("blend_confluence").first["x"] == 250
    apply(service, "set_style", id="blend_confluence", style={"visible": False})
    assert service.geometry_scene(0).list_objects() == [
        "island_lagoon",
        "island_lowtide",
        "island_glass",
    ]
    apply(service, "select", ids=["blend_confluence"])
    apply(service, "delete_blend", id="blend_confluence")
    assert service.snapshot()["selection"] == []
    assert service.recipe()["layer_order"] == [
        i for i in original["layer_order"] if i != "blend_confluence"
    ]
    apply(service, "create_geometry", name="New front layer")
    assert service.recipe()["layer_order"][-1] == service.recipe()["objects"][-1]["id"]
    apply(service, "undo")
    apply(service, "undo")
    assert service.recipe()["layer_order"] == original["layer_order"]
    assert not service.recipe()["blends"][0]["style"]["visible"]


@pytest.mark.parametrize(
    "filename",
    [
        "tidal_atlas_recipe.json",
        "tidal_atlas_choreography.json",
        "tidal_atlas_confluence.json",
    ],
)
def test_legacy_migration_preserves_drawing_order_tracks_styles_and_fields(
    filename, tmp_path
):
    legacy = json.loads((ROOT / "examples" / filename).read_text())
    frozen = copy.deepcopy(legacy)
    migrated = Recipe.model_validate(legacy).model_dump()
    assert legacy == frozen and migrated["schema_version"] == 4
    assert migrated["layer_order"] == [o["id"] for o in legacy["objects"]] + [
        b["id"] for b in legacy.get("blends", [])
    ]
    assert migrated["blends"] == legacy.get("blends", [])
    for old, new in zip(legacy["objects"], migrated["objects"]):
        assert new == {**old, "keyframes": old.get("keyframes", [])}
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps({**legacy, "document_id": "legacy_doc", "revision": 5}))
    assert SceneService(path).recipe() == migrated
    malformed = {**migrated}
    malformed.pop("layer_order")
    with pytest.raises(ValueError):
        Recipe.model_validate(malformed)


def test_layered_demo_reproducibility():
    result = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            "import {layeredDemoRecipe} from './studio/static/layered-demo.js';console.log(JSON.stringify(layeredDemoRecipe))",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    assert json.loads(result.stdout) == DEMO == Recipe.model_validate(DEMO).model_dump()
