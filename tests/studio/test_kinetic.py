"""Contract and cross-runtime checks for the standalone tidal recipe engine."""

import ast
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

# Import this standalone module without triggering geometry/__init__.py, whose
# legacy public API intentionally loads the existing symbolic/plotting stack.
ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "tidal_kinetic", ROOT / "geometry/kinetic.py"
)
kinetic = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kinetic)

FIXTURE = {
    "x": 345,
    "y": 380,
    "radius": 230,
    "elongation": 1.2,
    "rotation": -25,
    "lobes": 3,
    "warp": 0.78,
    "phase": 0.4,
}
FIXTURE_POINTS = [
    [601.0132297857397, 253.1115355110934],
    [264.35594286971843, 596.0225510535042],
    [278.3934823504277, 276.60141761535135],
    [315.7763103413383, 396.77123147402415],
]
FIXTURE_FIELDS = [-0.9921165404257253, -0.3895297549968011, 1.5723841657252473]


def _studio_contract():
    """Inspect numeric schema defaults without importing optional app dependencies."""
    tree = ast.parse((ROOT / "studio/service.py").read_text())
    schema = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Parameters"
    )
    bounds = {}
    for field in schema.body:
        if not isinstance(field, ast.AnnAssign):
            continue
        limits = {}
        for keyword in field.value.keywords:
            if keyword.arg not in {"ge", "le"}:
                continue
            limits[keyword.arg] = (
                math.tau
                if isinstance(keyword.value, ast.Attribute)
                and keyword.value.attr == "tau"
                else ast.literal_eval(keyword.value)
            )
        bounds[field.target.id] = (limits["ge"], limits["le"])
    initial = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "initial_recipe"
    )
    defaults = [
        {keyword.arg: ast.literal_eval(keyword.value) for keyword in node.keywords}
        for node in ast.walk(initial)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Parameters"
    ]
    return bounds, defaults


def test_studio_schema_bounds_match_standalone_contract():
    bounds, defaults = _studio_contract()
    assert bounds == kinetic.PARAMETER_BOUNDS
    assert len(defaults) >= 2
    for parameters in defaults:
        assert kinetic.normalize_parameters(parameters) == parameters


def _run_javascript(payload):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is needed for the explicit Python/JavaScript parity check")
    # Import as a data URL so no package.json/module-mode mutation is required.
    script = """
      import fs from 'node:fs';
      const source = fs.readFileSync(process.argv[1], 'utf8');
      const g = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
      const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
      const cases = payload.cases.map(c => ({
        contours: g.generateContours(c.parameters, c.time, c.motion, c.count, c.samples),
        fields: payload.probes.map(([x,y]) => g.evaluate(x,y,c.parameters,c.time,c.motion)),
        recipe: g.toRecipe(g.fromRecipe(g.toRecipe(c.parameters))),
      }));
      const rejected = payload.invalid.map(p => {
        try { g.normalizeParameters(p); return false; } catch { return true; }
      });
      console.log(JSON.stringify({cases, rejected}));
    """
    result = subprocess.run(
        [
            node,
            "--input-type=module",
            "-e",
            script,
            str(ROOT / "studio/static/geometry.js"),
        ],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
        timeout=20,
    )
    return json.loads(result.stdout)


def test_known_geometry_fixture():
    contours = kinetic.generate_contours(FIXTURE, 12.5, 0.65, 5, 48)
    actual = [contours[0][0], contours[0][17], contours[2][31], contours[4][13]]
    np.testing.assert_allclose(actual, FIXTURE_POINTS, rtol=0, atol=1e-10)
    actual_fields = [
        kinetic.evaluate(x, y, FIXTURE, 12.5, 0.65)
        for x, y in [(345, 380), (500, 400), (10, 10)]
    ]
    np.testing.assert_allclose(actual_fields, FIXTURE_FIELDS, rtol=0, atol=1e-12)


def test_python_javascript_formula_parity():
    cases = [
        {
            "parameters": FIXTURE,
            "time": 12.5,
            "motion": 0.65,
            "count": 5,
            "samples": 48,
        },
        {"parameters": {}, "time": 0, "motion": 0.45, "count": 24, "samples": 180},
        {
            "parameters": {
                "warp": 1,
                "lobes": 9,
                "phase": math.tau,
                "radius": 400,
                "elongation": 0.4,
            },
            "time": -23.8,
            "motion": 1,
            "count": 8,
            "samples": 90,
        },
        {
            "parameters": {"rotation": 360, "x": -1000, "y": 1400, "elongation": 2.5},
            "time": 1e9,
            "motion": 0,
            "count": 3,
            "samples": 24,
        },
        {
            "parameters": {"radius": 1000, "warp": -1, "lobes": 4.5},
            "time": 10,
            "motion": 2,
            "count": 1,
            "samples": 12,
        },
    ]
    cases.extend(
        {
            "parameters": parameters,
            "time": 3.25,
            "motion": 0.45,
            "count": 26,
            "samples": 180,
        }
        for parameters in _studio_contract()[1]
    )
    probes = [(345, 380), (500, 400), (10, 10), (-1000, 1400), (1e9, -1e9)]
    invalid = [
        {"callback": "sin(x)"},
        {"radius": "250"},
        {"warp": True},
        [],
        {"phase": None},
    ]
    result = _run_javascript({"cases": cases, "probes": probes, "invalid": invalid})
    assert all(result["rejected"])
    for case, actual in zip(cases, result["cases"]):
        expected = kinetic.generate_contours(**case)
        np.testing.assert_allclose(actual["contours"], expected, rtol=0, atol=8e-10)
        expected_fields = [
            kinetic.evaluate(x, y, case["parameters"], case["time"], case["motion"])
            for x, y in probes
        ]
        np.testing.assert_allclose(
            actual["fields"], expected_fields, rtol=2e-13, atol=2e-12
        )
        assert actual["recipe"] == kinetic.to_recipe(case["parameters"])


def test_contour_samples_match_implicit_levels():
    for parameters, time in [
        (FIXTURE, 8.5),
        ({"warp": 1, "lobes": 9, "elongation": 2.5}, -20),
    ]:
        contours = kinetic.generate_contours(parameters, time, 1, count=32, samples=360)
        for level, contour in zip(kinetic.contour_levels(32), contours):
            values = kinetic.evaluate(contour[:, 0], contour[:, 1], parameters, time, 1)
            np.testing.assert_allclose(values, level - 1, rtol=0, atol=2e-13)


def test_finite_closed_and_bounded_across_parameter_extremes():
    for lobes in range(2, 10):
        for phase in np.linspace(0, math.tau, 9):
            for elongation, warp in [(0.4, 0), (0.4, 1), (2.5, 1)]:
                parameters = dict(
                    FIXTURE,
                    lobes=lobes,
                    phase=phase,
                    elongation=elongation,
                    warp=warp,
                    radius=400,
                )
                contours = kinetic.generate_contours(parameters, phase * 30, 1, 8, 180)
                points = np.asarray(contours)
                assert points.shape == (8, 181, 2)
                assert np.all(np.isfinite(points))
                np.testing.assert_array_equal(points[:, 0], points[:, -1])
                stretch = max(math.sqrt(elongation), 1 / math.sqrt(elongation))
                conservative_bound = 400 * (1.32 * stretch + 0.04)
                assert (
                    np.max(
                        np.linalg.norm(
                            points - [parameters["x"], parameters["y"]], axis=-1
                        )
                    )
                    < conservative_bound
                )


def test_nested_levels_have_decreasing_sampled_area():
    contours = kinetic.generate_contours(FIXTURE, 18, 1, 40, 720)
    areas = []
    for contour in contours:
        areas.append(
            0.5
            * np.sum(
                contour[:-1, 0] * contour[1:, 1] - contour[1:, 0] * contour[:-1, 1]
            )
        )
    assert np.all(np.asarray(areas) > 0)
    assert np.all(np.diff(areas) < 0)
    # The continuous radial twist and reciprocal-axis stretch preserve area;
    # sampled polygons approximate that relationship rather than claiming it.
    np.testing.assert_allclose(
        np.asarray(areas) / areas[0], kinetic.contour_levels(40) ** 2, rtol=8e-4, atol=0
    )


def test_animation_is_deterministic_and_motion_zero_is_static():
    p = dict(FIXTURE)
    first = kinetic.generate_contours(p, 12.5, 0.6)
    repeated = kinetic.generate_contours(p, 12.5, 0.6)
    np.testing.assert_array_equal(first, repeated)
    np.testing.assert_array_equal(
        kinetic.generate_contours(p, 0, 0), kinetic.generate_contours(p, 1e12, 0)
    )
    assert not np.array_equal(first, kinetic.generate_contours(p, 13, 0.6))
    assert p == FIXTURE
    period = kinetic.LOOP_DURATION
    np.testing.assert_allclose(
        first, kinetic.generate_contours(p, 12.5 + period, 0.6), rtol=0, atol=2e-12
    )
    # Check the modulo seam as well as one ordinary adjacent animation frame.
    for time in [12.5, period - 1 / 60]:
        current = np.asarray(kinetic.generate_contours(p, time, 1))
        following = np.asarray(kinetic.generate_contours(p, time + 1 / 60, 1))
        assert np.max(np.linalg.norm(current - following, axis=-1)) < 0.8


def test_numeric_recipe_json_roundtrip():
    original = kinetic.to_recipe(FIXTURE)
    restored = kinetic.from_recipe(json.loads(json.dumps(original, allow_nan=False)))
    assert restored == kinetic.normalize_parameters(FIXTURE)
    np.testing.assert_array_equal(
        kinetic.generate_contours(restored), kinetic.generate_contours(FIXTURE)
    )
    original["parameters"]["radius"] = 81
    assert FIXTURE["radius"] == 230
    with pytest.raises(ValueError):
        kinetic.from_recipe({"type": "python", "version": 1, "parameters": {}})
    with pytest.raises(ValueError):
        kinetic.from_recipe({"type": "tidal_island", "version": True, "parameters": {}})
    with pytest.raises(ValueError):
        kinetic.from_recipe(dict(kinetic.to_recipe(), expression="eval(x)"))
    with pytest.raises(ValueError):
        kinetic.from_recipe(dict(kinetic.to_recipe(), parameters=None))


@pytest.mark.parametrize(
    "bad", [float("nan"), float("inf"), -float("inf"), True, "240", None, lambda: 1]
)
def test_invalid_parameter_values_are_rejected(bad):
    with pytest.raises(ValueError):
        kinetic.generate_contours({"radius": bad})


def test_limits_prevent_unbounded_output():
    normalized = kinetic.normalize_parameters(
        {"radius": 1e20, "x": -1e20, "y": 1e20, "warp": -20, "lobes": 4.5}
    )
    assert normalized["radius"] == 400
    assert normalized["x"] == -1000
    assert normalized["y"] == 1400
    assert normalized["warp"] == 0
    assert normalized["lobes"] == 5
    contours = kinetic.generate_contours({}, count=10**9, samples=10**9)
    assert np.asarray(contours).shape == (80, 721, 2)
    assert np.asarray(kinetic.generate_contours({}, count=-10, samples=-10)).shape == (
        2,
        25,
        2,
    )
    for key in ["count", "samples"]:
        with pytest.raises(ValueError):
            kinetic.generate_contours({}, **{key: 2.5})
    for key in ["time", "motion"]:
        with pytest.raises(ValueError):
            kinetic.generate_contours({}, **{key: math.nan})


def test_field_scalar_broadcast_and_input_bounds():
    assert isinstance(kinetic.evaluate(500, 350), float)
    field = kinetic.evaluate(
        np.linspace(0, 1000, 17)[:, None], np.linspace(0, 700, 9)[None, :]
    )
    assert field.shape == (17, 9)
    assert np.all(np.isfinite(field))
    assert math.isfinite(kinetic.evaluate(1e9, -1e9))
    with pytest.raises(ValueError):
        kinetic.evaluate(np.zeros((2001, 1)), np.zeros((1, 2001)))
    for bad in [math.nan, math.inf, 1e10, "5", True, None]:
        with pytest.raises(ValueError):
            kinetic.evaluate(bad, 0)


def test_standalone_module_has_only_numpy_and_stdlib_imports():
    tree = ast.parse((ROOT / "geometry/kinetic.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "math", "collections", "numbers", "numpy"}
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"eval", "exec", "compile"}
        for node in ast.walk(tree)
    )
