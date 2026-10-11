"""Bounded, deterministic pose sampling; independent of editor and wall clocks."""

import math
from numbers import Real

from .kinetic import LOOP_DURATION, PARAMETER_BOUNDS, normalize_parameters

POSE_FIELDS = ("x", "y", "radius", "elongation", "rotation", "warp")
MAX_KEYFRAMES = 24


def validate_keyframes(keyframes):
    """Validate sorted, complete numeric poses without clamping authored values."""
    if not isinstance(keyframes, list) or len(keyframes) > MAX_KEYFRAMES:
        raise ValueError("An island supports at most 24 keyframes")
    previous = -1.0
    for key in keyframes:
        if not isinstance(key, dict) or set(key) != {"time", "parameters", "easing"}:
            raise ValueError("Invalid keyframe fields")
        time = key["time"]
        if (
            isinstance(time, bool)
            or not isinstance(time, Real)
            or not math.isfinite(time)
            or not previous < time <= LOOP_DURATION
        ):
            raise ValueError(
                "Keyframe times must be unique, increasing and within 0..12"
            )
        if (
            time < 0
            or not isinstance(key["easing"], str)
            or key["easing"] not in {"linear", "smooth"}
        ):
            raise ValueError("Invalid keyframe time or easing")
        pose = key["parameters"]
        if not isinstance(pose, dict) or set(pose) != set(POSE_FIELDS):
            raise ValueError("Keyframes require a complete six-parameter pose")
        for name, value in pose.items():
            low, high = PARAMETER_BOUNDS[name]
            if (
                isinstance(value, bool)
                or not isinstance(value, Real)
                or not math.isfinite(value)
                or not low <= value <= high
            ):
                raise ValueError(f"Invalid keyframe parameter: {name}")
        previous = time


def sample_parameters(parameters, keyframes=None, time=0.0):
    """Return a fresh pose. Hold endpoints; interpolate using the left key's easing.

    A paused 12-second playhead samples the authored endpoint. Times outside the
    first loop wrap. Match poses at 0 and 12 for a seamless playback join. Rotation
    interpolates authored degrees directly; no hidden shortest-path rotation.
    """
    if isinstance(time, bool) or not isinstance(time, Real) or not math.isfinite(time):
        raise ValueError("Time must be finite")
    result = normalize_parameters(parameters)
    keys = [] if keyframes is None else keyframes
    validate_keyframes(keys)
    if not keys:
        return result
    time = time if 0 <= time <= LOOP_DURATION else time % LOOP_DURATION
    left = right = keys[0]
    if time >= keys[-1]["time"]:
        left = right = keys[-1]
    elif time > keys[0]["time"]:
        for left, right in zip(keys, keys[1:]):
            if time <= right["time"]:
                break
    fraction = (
        (time - left["time"]) / (right["time"] - left["time"])
        if right["time"] != left["time"]
        else 0
    )
    if left["easing"] == "smooth":
        fraction = fraction * fraction * (3 - 2 * fraction)
    for name in POSE_FIELDS:
        result[name] = left["parameters"][name] + fraction * (
            right["parameters"][name] - left["parameters"][name]
        )
    return result
