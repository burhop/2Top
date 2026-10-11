"""Quantitative checks of the kinetic adapter through the existing engine."""

import json
import math

import numpy as np
import pytest

from geometry import (
    BaseField,
    BlendedField,
    CurveField,
    ImplicitCurve,
    KineticIslandCurve,
    KineticIslandField,
    ProceduralCurve,
    RFunctionCurve,
)
from geometry import kinetic
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management import SceneManager


@pytest.mark.parametrize(
    "parameters,time,motion",
    [
        ({}, 0, 0.45),
        ({"warp": 1, "lobes": 9, "elongation": 0.4}, -23.8, 1),
        ({"x": -1000, "y": 1400, "rotation": 360}, 1e9, 0),
        ({"radius": 1000, "warp": -1, "lobes": 4.5}, 10, 2),
    ],
)
def test_evaluation_matches_core_with_scalar_and_broadcast_inputs(
    parameters, time, motion
):
    field = KineticIslandField(parameters, time, motion)
    assert isinstance(field, BaseField)
    assert isinstance(field.evaluate(30, 200), float)
    assert field.evaluate(30, 200) == kinetic.evaluate(
        30, 200, parameters, time, motion
    )
    x = np.linspace(-1200, 1800, 13)[:, None]
    y = np.linspace(-700, 1600, 17)[None, :]
    np.testing.assert_array_equal(
        field.evaluate(x, y), kinetic.evaluate(x, y, parameters, time, motion)
    )
    assert field.evaluate(x, y).shape == (13, 17)


@pytest.mark.parametrize("radius", [80, 230, 400])
def test_radius_scaled_gradient_matches_independent_five_point_stencil(radius):
    field = KineticIslandField(
        {"radius": radius, "warp": 1, "lobes": 9, "elongation": 0.4},
        time=4.25,
        motion=0.8,
    )
    points = np.asarray(
        field.level_set(-0.2).get_polyline_approximation(resolution=96)
    )[:-1]
    x, y = points.T
    h = radius * 2e-5
    gx_reference = (
        -field.evaluate(x + 2 * h, y)
        + 8 * field.evaluate(x + h, y)
        - 8 * field.evaluate(x - h, y)
        + field.evaluate(x - 2 * h, y)
    ) / (12 * h)
    gy_reference = (
        -field.evaluate(x, y + 2 * h)
        + 8 * field.evaluate(x, y + h)
        - 8 * field.evaluate(x, y - h)
        + field.evaluate(x, y - 2 * h)
    ) / (12 * h)
    gx, gy = field.gradient(x, y)
    np.testing.assert_allclose(gx, gx_reference, rtol=2e-6, atol=2e-9)
    np.testing.assert_allclose(gy, gy_reference, rtol=2e-6, atol=2e-9)
    scalar = field.gradient(float(x[0]), float(y[0]))
    assert all(isinstance(value, float) for value in scalar)
    np.testing.assert_allclose(scalar, [gx[0], gy[0]], rtol=0, atol=0)


def test_gradient_scales_inversely_with_radius_and_is_translation_invariant():
    small = KineticIslandField({"x": 0, "y": 0, "radius": 80}, motion=0)
    large = KineticIslandField({"x": 1000, "y": 900, "radius": 400}, motion=0)
    x = np.array([0.31, 0.8, -0.75, 1.31])
    y = np.array([0.21, -0.63, 0.43, 0.15])
    small_gradient = np.asarray(small.gradient(x * 80, y * 80))
    large_gradient = np.asarray(large.gradient(1000 + x * 400, 900 + y * 400))
    np.testing.assert_allclose(
        small_gradient, large_gradient * 5, rtol=2e-8, atol=1e-10
    )


def test_gradient_broadcasts_and_stays_finite_at_coordinate_domain_boundary():
    field = KineticIslandField()
    gx, gy = field.gradient(np.array([-1e9, 350, 1e9])[:, None], np.array([-1e9, 1e9]))
    assert gx.shape == gy.shape == (3, 2)
    assert np.isfinite(gx).all() and np.isfinite(gy).all()


def test_contours_match_existing_core_and_have_zero_level_residual():
    parameters = {"warp": 0.98, "lobes": 9, "elongation": 2.5, "radius": 400}
    field = KineticIslandField(parameters, time=7.75, motion=0.9)
    contours = kinetic.generate_contours(parameters, 7.75, 0.9, count=11, samples=240)
    for radial_level, expected in zip(kinetic.contour_levels(11), contours):
        curve = field.level_set(float(radial_level - 1))
        assert isinstance(curve, ImplicitCurve)
        assert isinstance(curve, ProceduralCurve)
        assert curve.is_closed()
        points = np.asarray(curve.get_polyline_approximation(resolution=240))
        np.testing.assert_allclose(points, expected, rtol=0, atol=1e-11)
        np.testing.assert_allclose(curve.evaluate(*points.T), 0, rtol=0, atol=2e-14)
        np.testing.assert_array_equal(points[0], points[-1])


@pytest.mark.parametrize("level", [-0.99, -0.31, 0, 0.73, 16])
def test_arbitrary_level_sampling_and_conservative_bounds(level):
    curve = KineticIslandCurve(
        {"warp": 1, "lobes": 9, "elongation": 0.4, "rotation": 157},
        time=2.8,
        motion=1,
        level=level,
    )
    points = np.asarray(curve.get_polyline_approximation((-1, 1, -1, 1), 720))
    np.testing.assert_allclose(curve.evaluate(*points.T), 0, rtol=0, atol=2e-12)
    xmin, xmax, ymin, ymax = curve.bounding_box()
    assert np.all((xmin <= points[:, 0]) & (points[:, 0] <= xmax))
    assert np.all((ymin <= points[:, 1]) & (points[:, 1] <= ymax))
    np.testing.assert_array_equal(
        curve.gradient(410, 230), curve.field.gradient(410, 230)
    )


def test_empty_degenerate_and_bounded_sampling_cases():
    field = KineticIslandField()
    empty = field.level_set(-2)
    assert empty.get_polyline_approximation() == []
    assert empty.bounding_box() is None
    assert not empty.is_closed()
    point = field.level_set(-1)
    samples = point.get_polyline_approximation()
    assert len(samples) == 1
    assert point.evaluate(*samples[0]) == 0
    assert not point.is_closed()
    assert len(field.level_set().get_polyline_approximation(resolution=1)) == 25
    assert len(field.level_set().get_polyline_approximation(resolution=10000)) == 721
    with pytest.raises(ValueError):
        field.level_set().get_polyline_approximation(resolution=25.5)


def test_snapshots_do_not_alias_input_exported_or_returned_parameters():
    parameters = {"radius": 130}
    field = KineticIslandField(parameters, time=-0.5, motion=2)
    curve = field.level_set(-0.25)
    baseline = curve.evaluate(325, 190)
    parameters["radius"] = 350
    exported = curve.to_dict()
    exported["parameters"]["radius"] = 400
    visible = field.parameters
    visible["radius"] = 80
    assert field.parameters["radius"] == curve.parameters["radius"] == 130
    assert curve.evaluate(325, 190) == baseline
    assert field.time == 11.5
    assert field.motion == 1
    with pytest.raises(AttributeError):
        field.time = 4
    with pytest.raises(AttributeError):
        curve.level = 0


@pytest.mark.parametrize("level", [None, -0.3])
def test_own_json_roundtrip_preserves_all_numeric_state(level):
    field = KineticIslandField({"phase": math.tau, "radius": 318}, -31.25, 0.68)
    original = field if level is None else field.level_set(level)
    data = json.loads(json.dumps(original.to_dict(), allow_nan=False))
    restored = type(original).from_dict(data)
    assert restored.to_dict() == data
    x, y = np.meshgrid(np.linspace(50, 1000, 21), np.linspace(25, 800, 17))
    np.testing.assert_array_equal(restored.evaluate(x, y), original.evaluate(x, y))
    np.testing.assert_array_equal(restored.gradient(x, y), original.gradient(x, y))
    assert "expression" not in data and "function" not in data
    assert "_serialization_note" not in data


@pytest.mark.parametrize("factory", [KineticIslandField, KineticIslandCurve])
@pytest.mark.parametrize(
    "mutation",
    [
        lambda data: data.update(expression="__import__('os').system('echo bad')"),
        lambda data: data.update(function="lambda x,y: 0"),
        lambda data: data.update(version=True),
        lambda data: data.update(version=1.0),
        lambda data: data.update(version=2),
        lambda data: data.update(type="ProceduralCurve"),
        lambda data: data.update(parameters=None),
        lambda data: data.update(parameters={"callback": "sin(x)"}),
        lambda data: data.update(parameters={"radius": "240"}),
        lambda data: data.update(parameters={"warp": True}),
        lambda data: data.update(time=float("nan")),
        lambda data: data.update(motion=float("inf")),
    ],
)
def test_recipe_loaders_reject_executable_unknown_and_nonfinite_data(factory, mutation):
    data = factory().to_dict()
    mutation(data)
    with pytest.raises(ValueError):
        factory.from_dict(data)


@pytest.mark.parametrize("level", [-17, 17, float("nan"), float("inf"), True, "0"])
def test_rejects_invalid_levels(level):
    with pytest.raises(ValueError):
        KineticIslandField().level_set(level)
    data = KineticIslandCurve().to_dict()
    data["level"] = level
    with pytest.raises(ValueError):
        ImplicitCurve.from_dict(data)


@pytest.mark.parametrize("x,y", [("2", 3), (True, 3), (float("nan"), 3), (1e10, 3)])
def test_gradient_does_not_bypass_core_coordinate_validation(x, y):
    with pytest.raises(ValueError):
        KineticIslandField().gradient(x, y)


def test_existing_curve_field_and_rfunction_interfaces_and_nested_roundtrip():
    field = KineticIslandField({"x": 320}, time=5.2)
    curve = field.level_set(-0.17)
    wrapped = CurveField(curve)
    other = KineticIslandField({"x": 680}, time=1.8)
    blended = BlendedField([field, wrapped, other], operation="average")
    combined_curve = RFunctionCurve(curve, other.level_set(), "union")
    x = np.array([0, 320, 500, 680, 1000])
    y = np.array([200, 350, 425, 350, 600])
    np.testing.assert_array_equal(wrapped.evaluate(x, y), curve.evaluate(x, y))
    np.testing.assert_array_equal(wrapped.gradient(x, y), curve.gradient(x, y))
    np.testing.assert_allclose(
        blended.evaluate(x, y),
        (field.evaluate(x, y) + curve.evaluate(x, y) + other.evaluate(x, y)) / 3,
    )
    np.testing.assert_allclose(
        blended.gradient(x, y),
        (np.asarray(field.gradient(x, y)) * 2 + np.asarray(other.gradient(x, y))) / 3,
    )
    np.testing.assert_array_equal(
        combined_curve.evaluate(x, y),
        np.minimum(curve.evaluate(x, y), other.evaluate(x, y)),
    )
    for original, loader in [
        (curve, ImplicitCurve.from_dict),
        (wrapped, CurveField.from_dict),
        (blended, BlendedField.from_dict),
        (combined_curve, ImplicitCurve.from_dict),
    ]:
        restored = loader(json.loads(json.dumps(original.to_dict())))
        assert restored.to_dict() == original.to_dict()
        np.testing.assert_array_equal(restored.evaluate(x, y), original.evaluate(x, y))
        np.testing.assert_allclose(restored.gradient(x, y), original.gradient(x, y))


def test_curve_field_level_set_preserves_declarative_shift_and_validates_sum():
    original = KineticIslandField({"radius": 195}, time=4.5, motion=0.8).level_set(-0.2)
    wrapped = CurveField(original)
    shifted = wrapped.level_set(0.3)
    assert isinstance(shifted, KineticIslandCurve)
    assert shifted.level == pytest.approx(0.1)
    assert shifted.parameters == original.parameters
    assert shifted.time == original.time
    assert shifted.motion == original.motion
    x, y = np.array([200, 400, 600]), np.array([125, 350, 575])
    np.testing.assert_allclose(shifted.evaluate(x, y), wrapped.evaluate(x, y) - 0.3)
    restored = ImplicitCurve.from_dict(json.loads(json.dumps(shifted.to_dict())))
    np.testing.assert_array_equal(restored.evaluate(x, y), shifted.evaluate(x, y))
    assert CurveField(KineticIslandCurve(level=-16)).level_set(32).level == 16
    for invalid in [float("nan"), "0.2", True, -16, 17]:
        with pytest.raises(ValueError):
            wrapped.level_set(invalid)


def test_real_scene_persistence_and_graphics_backend_paths_and_grids(tmp_path):
    field = KineticIslandField({"x": 450, "radius": 180}, time=2.75, motion=0.82)
    curve = field.level_set(-0.32)
    scene = SceneManager()
    scene.add_object("island", curve, {"color": "#123456", "linewidth": 1.3})
    scene.add_object("scalar", field)
    scene.add_object("wrapped", CurveField(curve))
    scene.add_object("blended", BlendedField([field, CurveField(curve)], "average"))
    path = tmp_path / "kinetic-engine-scene.json"
    scene.save_scene(str(path))
    restored = SceneManager()
    restored.load_scene(str(path))
    assert restored.list_objects() == scene.list_objects()
    for name in scene.list_objects():
        assert restored.get_object(name).to_dict() == scene.get_object(name).to_dict()
        assert restored.get_object(name).evaluate(510, 310) == scene.get_object(
            name
        ).evaluate(510, 310)
    backend = GraphicsBackendInterface(restored)
    bounds = (0, 1000, 0, 700)
    paths = backend.get_curve_paths(bounds, resolution=96)
    assert "error" not in paths["island"]
    assert paths["island"]["closed"] is True
    assert paths["island"]["point_count"] == 97
    assert paths["island"]["style"]["color"] == "#123456"
    np.testing.assert_array_equal(
        paths["island"]["points"], curve.get_polyline_approximation(resolution=96)
    )
    assert paths["scalar"]["type"] == "field"
    grids = backend.get_field_data(bounds, resolution=(27, 19))
    x, y = np.meshgrid(np.linspace(0, 1000, 27), np.linspace(0, 700, 19))
    np.testing.assert_array_equal(grids["scalar"]["data"], field.evaluate(x, y))
    np.testing.assert_array_equal(grids["island"]["data"], curve.evaluate(x, y))
    assert grids["scalar"]["statistics"]["finite_count"] == 27 * 19
