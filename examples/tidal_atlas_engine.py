"""Use studio artwork through 2Top's existing engine, without a browser or AI.

Run from the repository root: python -m examples.tidal_atlas_engine
"""

import json

import numpy as np

from geometry import BlendedField, CurveField, ImplicitCurve, KineticIslandField
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management import SceneManager


def main():
    field = KineticIslandField(
        {"x": 350, "y": 350, "radius": 200, "warp": 0.7}, time=3, motion=0.45
    )
    shore = field.level_set(0)
    restored = ImplicitCurve.from_dict(json.loads(json.dumps(shore.to_dict())))
    scene = SceneManager()
    scene.add_object("my-island", restored, {"color": "#f0a088"})
    paths = GraphicsBackendInterface(scene).get_curve_paths(
        bounds=(0, 1000, 0, 700), resolution=180
    )
    points = np.asarray(paths["my-island"]["points"])
    residual = np.abs(field.evaluate(points[:, 0], points[:, 1])).max()
    layered = BlendedField([field, CurveField(restored)], operation="average")
    print(f"Existing renderer extracted {len(points)} shoreline points.")
    print(f"Maximum dimensionless field residual: {residual:.3g}")
    print(f"Existing field composition at (350,350): {layered.evaluate(350, 350):.3g}")
    print("The field is not a Euclidean signed distance; curves are sampled.")


if __name__ == "__main__":
    main()
