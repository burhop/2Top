"""Pure whole-choreography transforms; existing geometry formulas stay unchanged."""

import math

from geometry.kinetic import PARAMETER_BOUNDS


def resolve_islands(scene, layer_ids):
    """Expand selected blends to retained operands and transform shared sources once."""
    layers = {item["id"]: item for item in [*scene["objects"], *scene["blends"]]}
    targets = set()
    for layer_id in layer_ids:
        if layer_id not in layers:
            raise KeyError(layer_id)
        layer = layers[layer_id]
        targets.update(
            [layer["id"]]
            if "parameters" in layer
            else [layer["source_a"], layer["source_b"]]
        )
    available = {island["id"] for island in scene["objects"]}
    if targets - available:
        raise KeyError(sorted(targets - available)[0])
    return [island for island in scene["objects"] if island["id"] in targets]


def transform_pose(pose, *, dx=0, dy=0, scale=1, rotation=0, pivot):
    """Scale then rotate about pivot, then translate; preserve authored degrees."""
    result = dict(pose)
    if scale == 1 and rotation == 0:
        result["x"], result["y"] = pose["x"] + dx, pose["y"] + dy
    else:
        angle = math.radians(rotation)
        cosine, sine = math.cos(angle), math.sin(angle)
        x, y = (pose["x"] - pivot["x"]) * scale, (pose["y"] - pivot["y"]) * scale
        result["x"] = pivot["x"] + x * cosine - y * sine + dx
        result["y"] = pivot["y"] + x * sine + y * cosine + dy
    result["radius"] = pose["radius"] * scale
    result["rotation"] = pose["rotation"] + rotation
    for name in ("x", "y", "radius", "rotation"):
        lower, upper = PARAMETER_BOUNDS[name]
        if not math.isfinite(result[name]) or not lower <= result[name] <= upper:
            raise ValueError(
                f"Whole-path transform exceeds {name} limits ({lower}..{upper}); use a smaller change"
            )
    return result


def transformed_islands(islands, *, dx=0, dy=0, scale=1, rotation=0, pivot=None):
    """Return complete transformed copies, validating every pose before mutation."""
    if not islands:
        raise ValueError("Choose at least one island or blend")
    pivot = pivot or {
        name: sum(island["parameters"][name] for island in islands) / len(islands)
        for name in ("x", "y")
    }
    kwargs = dict(dx=dx, dy=dy, scale=scale, rotation=rotation, pivot=pivot)
    return [
        {
            **island,
            "style": dict(island["style"]),
            "parameters": transform_pose(island["parameters"], **kwargs),
            "keyframes": [
                {**key, "parameters": transform_pose(key["parameters"], **kwargs)}
                for key in island["keyframes"]
            ],
        }
        for island in islands
    ]
