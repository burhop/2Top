"""Atomic translation/scaling of explicit motion times; geometry is unchanged."""

import copy

from geometry.choreography import validate_keyframes


class RetimeError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def retimed_islands(scene, targets, delta):
    return _retimed_islands(scene, targets, lambda time: time + delta)


def scaled_time(time, anchor, factor):
    """Keep identity and anchored keys exact, including fractional source times."""
    return time if factor == 1 or time == anchor else anchor + (time - anchor) * factor


def scaled_islands(scene, targets, anchor, factor):
    return _retimed_islands(
        scene, targets, lambda time: scaled_time(time, anchor, factor)
    )


def _retimed_islands(scene, targets, map_time):
    """Resolve exact source times, vacate them together, then check all destinations."""
    islands = {island["id"]: island for island in scene["objects"]}
    changed = []
    for target in targets:
        island = islands.get(target["id"])
        if island is None:
            raise RetimeError(
                "object_not_found", "Select an existing island track", 404
            )
        source_times = set(target["times"])
        existing = {key["time"] for key in island["keyframes"]}
        if not source_times <= existing:
            raise RetimeError(
                "keyframe_not_found",
                "No keyframe at one of the exact source times",
                404,
            )
        untouched = existing - source_times
        mapping = {time: map_time(time) for time in source_times}
        destinations = list(mapping.values())
        if any(not 0 <= time <= 12 for time in destinations):
            raise RetimeError(
                "keyframe_range", "Every retimed key must stay within 0..12 seconds"
            )
        if len(set(destinations)) != len(destinations) or any(
            time in untouched for time in destinations
        ):
            raise RetimeError(
                "keyframe_collision",
                "Retimed keys collide with another destination or an unselected pose",
            )
        result = copy.deepcopy(island)
        for key in result["keyframes"]:
            if key["time"] in source_times:
                key["time"] = mapping[key["time"]]
        result["keyframes"].sort(key=lambda key: key["time"])
        validate_keyframes(result["keyframes"])
        changed.append(result)
    return changed
