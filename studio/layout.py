"""Deterministic center layout through existing whole-path translations."""

from geometry.choreography import sample_parameters
from studio.transforms import transformed_islands

MODES = {"align_x", "align_y", "space_x", "space_y"}


def layout_plan(scene, ids, mode, time=0):
    """Align means or space stable center order, keeping the outer centers fixed."""
    if mode not in MODES:
        raise ValueError("Choose a supported center layout")
    if len(ids) < 2 or len(ids) > 16 or len(ids) != len(set(ids)):
        raise ValueError("Choose 2..16 unique island IDs")
    if mode.startswith("space") and len(ids) < 3:
        raise ValueError("Even spacing needs at least three islands")
    islands = {island["id"]: island for island in scene["objects"]}
    for key in ids:
        if key not in islands:
            if any(blend["id"] == key for blend in scene["blends"]):
                raise ValueError(
                    "Center layout accepts islands only; select retained sources instead of a blend"
                )
            raise KeyError(key)
    axis = mode[-1]
    anchors = {
        key: sample_parameters(
            islands[key]["parameters"], islands[key]["keyframes"], time
        )
        for key in ids
    }
    targets = {}
    if mode.startswith("align"):
        # Stable summation/order makes a reversed selection produce the same plan.
        values = [anchors[key][axis] for key in sorted(ids)]
        mean = (
            values[0]
            if all(value == values[0] for value in values)
            else sum(values) / len(ids)
        )
        targets = dict.fromkeys(ids, mean)
    else:
        ordered = sorted(ids, key=lambda key: (anchors[key][axis], key))
        low, high = anchors[ordered[0]][axis], anchors[ordered[-1]][axis]
        for index, key in enumerate(ordered):
            targets[key] = (
                low
                if index == 0
                else high
                if index == len(ordered) - 1
                else low + (high - low) * index / (len(ordered) - 1)
            )
    return [
        {
            "id": key,
            "dx": targets[key] - anchors[key]["x"] if axis == "x" else 0,
            "dy": targets[key] - anchors[key]["y"] if axis == "y" else 0,
        }
        for key in sorted(ids)
    ]


def laid_out_islands(scene, ids, mode, time=0):
    plan = layout_plan(scene, ids, mode, time)
    islands = {island["id"]: island for island in scene["objects"]}
    # Construct and validate every complete translation before changing the scene.
    return [
        transformed_islands([islands[move["id"]]], dx=move["dx"], dy=move["dy"])[0]
        for move in plan
    ]
