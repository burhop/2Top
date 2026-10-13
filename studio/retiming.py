"""Atomic time translation of explicit motion keys; geometry is unchanged."""

import copy

from geometry.choreography import validate_keyframes


class RetimeError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def retimed_islands(scene, targets, delta):
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
        destinations = [time + delta for time in source_times]
        if any(not 0 <= time <= 12 for time in destinations):
            raise RetimeError(
                "keyframe_range", "Every shifted key must stay within 0..12 seconds"
            )
        if len(set(destinations)) != len(destinations) or any(
            time in untouched for time in destinations
        ):
            raise RetimeError(
                "keyframe_collision",
                "Shifted keys collide with another destination or an unselected pose",
            )
        result = copy.deepcopy(island)
        for key in result["keyframes"]:
            if key["time"] in source_times:
                key["time"] += delta
        result["keyframes"].sort(key=lambda key: key["time"])
        validate_keyframes(result["keyframes"])
        changed.append(result)
    return changed
