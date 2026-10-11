"""Existing-key position/retiming edits preserve poses and shared transactions."""

import copy
import json
import subprocess
from pathlib import Path

import pytest

from geometry.choreography import sample_parameters
from studio.service import Recipe, SceneError, SceneService

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


def test_crossing_retime_preserves_pose_interpolation_and_undo(authored):
    before = authored.recipe()
    obj = before["objects"][0]
    original = obj["keyframes"][1]
    apply(
        authored,
        "edit_keyframe",
        id=obj["id"],
        time=3,
        new_time=7.5,
        position={"x": 550, "y": 150},
    )
    changed = authored.recipe()["objects"][0]
    assert [key["time"] for key in changed["keyframes"]] == [0, 6, 7.5, 9, 12]
    moved = changed["keyframes"][2]
    assert moved == {
        **original,
        "time": 7.5,
        "parameters": {**original["parameters"], "x": 550, "y": 150},
    }
    assert changed["parameters"] == obj["parameters"]
    for time in [0, 3.75, 6, 7.5, 12, 27]:
        expected = sample_parameters(changed["parameters"], changed["keyframes"], time)
        assert authored.get_geometry(obj["id"], time_value=time).parameters == expected
    saved = authored.recipe()
    apply(authored, "undo")
    assert authored.recipe() == before
    apply(authored, "redo")
    assert authored.recipe() == saved
    assert SceneService(authored._storage).recipe() == saved


@pytest.mark.parametrize(
    "edit",
    [
        {"time": 3, "new_time": 6},
        {"time": 12, "new_time": 0},
        {"time": 4, "new_time": 5},
        {"time": 3, "new_time": -0.01},
        {"time": 3, "new_time": 12.01},
        {"time": 3, "new_time": float("nan")},
        {"time": 3, "new_time": True},
        {"time": "3", "new_time": 4},
        {"time": 3},
        {"time": 3, "position": {"x": 350}},
        {"time": 3, "position": {"x": 350, "y": float("inf")}},
        {"time": 3, "position": {"x": -1001, "y": 350}},
        {"time": 3, "position": {"x": 350, "y": 350, "radius": 200}},
    ],
)
def test_invalid_motion_edits_leave_revision_history_and_disk_unchanged(authored, edit):
    before = authored.snapshot()
    disk = authored._storage.read_bytes()
    with pytest.raises(SceneError):
        apply(authored, "edit_keyframe", id=before["objects"][0]["id"], **edit)
    assert authored.snapshot() == before
    assert authored._storage.read_bytes() == disk


def test_atomic_collision_replay_stale_and_loop_endpoints(authored):
    obj = authored.recipe()["objects"][0]
    before = authored.snapshot()
    with pytest.raises(SceneError) as error:
        apply(
            authored,
            "batch",
            commands=[
                {
                    "op": "edit_keyframe",
                    "id": obj["id"],
                    "time": 0,
                    "position": {"x": 320, "y": 400},
                },
                {"op": "edit_keyframe", "id": obj["id"], "time": 3, "new_time": 6},
            ],
        )
    assert error.value.code == "keyframe_collision"
    assert authored.snapshot() == before
    args = {
        "id": obj["id"],
        "time": 12,
        "new_time": 11,
        "expected_revision": before["revision"],
        "request_id": "move_once",
    }
    result = authored.invoke("edit_keyframe", args, actor="mcp")
    assert authored.invoke("edit_keyframe", args, actor="mcp")["replayed"] is True
    with pytest.raises(SceneError) as error:
        authored.invoke(
            "edit_keyframe",
            {
                "id": obj["id"],
                "time": 11,
                "new_time": 12,
                "expected_revision": before["revision"],
            },
        )
    assert error.value.code == "revision_conflict"
    apply(authored, "edit_keyframe", id=obj["id"], time=11, new_time=12)
    assert authored.recipe()["objects"][0] == obj
    assert result["scene"]["objects"][0]["keyframes"][-1]["time"] == 11
    # 0 and 12 are distinct authored keys, even when their positions coincide.
    apply(
        authored, "edit_keyframe", id=obj["id"], time=0, position={"x": 350, "y": 350}
    )
    assert authored.recipe()["objects"][0]["keyframes"][-1] == obj["keyframes"][-1]


def test_schema_two_roundtrip_and_retimed_python_js_parity(authored):
    recipe = authored.recipe()
    frozen = copy.deepcopy(recipe)
    assert Recipe.model_validate(recipe).model_dump() == recipe == frozen
    apply(authored, "edit_keyframe", id=recipe["objects"][0]["id"], time=3, new_time=8)
    obj = authored.recipe()["objects"][0]
    cases = [
        {"parameters": obj["parameters"], "keys": obj["keyframes"], "time": t}
        for t in [0, 3, 6, 7, 8, 11.5, 12, 24]
    ]
    code = "import {sampleParameters} from './studio/static/choreography.js'; let s=''; for await(const x of process.stdin)s+=x; console.log(JSON.stringify(JSON.parse(s).map(c=>sampleParameters(c.parameters,c.keys,c.time))));"
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
    apply(authored, "load_recipe", recipe=authored.recipe())
    assert authored.recipe()["objects"][0] == obj
