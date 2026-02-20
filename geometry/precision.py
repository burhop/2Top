"""Precision and tolerance management utilities for geometry modules."""

from __future__ import annotations

import json
import math
import os
from contextlib import contextmanager
from dataclasses import dataclass, replace
from threading import RLock
from typing import Any, Dict, Optional

_DEFAULT_ABS = 1e-6
_DEFAULT_REL = 1e-5
_DEFAULT_ANGLE_DEG = 0.25
_DEFAULT_DISTANCE_FACTOR = 1e-4
_DEFAULT_ITER = 64
_ENV_KEY = "TWOTOP_PRECISION_POLICY"


@dataclass(frozen=True)
class PrecisionPolicy:
    """Container for all tolerance knobs used across geometry computations."""

    absolute: float = _DEFAULT_ABS
    relative: float = _DEFAULT_REL
    angular: float = math.radians(_DEFAULT_ANGLE_DEG)
    distance_factor: float = _DEFAULT_DISTANCE_FACTOR
    iteration_limit: int = _DEFAULT_ITER

    def with_updates(self, **overrides: Any) -> "PrecisionPolicy":
        """Return a copy with provided fields replaced."""

        return replace(self, **overrides)

    def blended_tolerance(self, scale_hint: Optional[float] = None) -> float:
        """Blend absolute/relative tolerances using an optional scale hint."""

        if scale_hint is None or not math.isfinite(scale_hint):
            return self.absolute
        scale = abs(scale_hint)
        rel_component = self.relative * max(scale, 1.0)
        return max(self.absolute, rel_component)

    def fuzzy_equal(self, value_a: float, value_b: float, scale_hint: Optional[float] = None) -> bool:
        """Return True if two values are equal within blended tolerance."""

        tol = self.blended_tolerance(scale_hint)
        return abs(value_a - value_b) <= tol

    def distance_threshold(self, scale_hint: Optional[float] = None) -> float:
        """Compute positional tolerance for distance comparisons."""

        scale = 1.0 if scale_hint is None else max(abs(scale_hint), 1.0)
        return max(self.absolute, self.distance_factor * scale)


_policy_lock = RLock()
_global_policy: PrecisionPolicy = PrecisionPolicy()
_policy_stack: list[PrecisionPolicy] = []


def _load_policy_from_env() -> Optional[PrecisionPolicy]:
    raw = os.getenv(_ENV_KEY)
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    allowed: Dict[str, Any] = {}
    for key in ("absolute", "relative", "angular", "distance_factor", "iteration_limit"):
        if key in payload:
            allowed[key] = payload[key]
    try:
        return PrecisionPolicy(**allowed)
    except (TypeError, ValueError):
        return None


def get_precision_policy() -> PrecisionPolicy:
    """Return the currently active precision policy."""

    global _global_policy
    with _policy_lock:
        return _policy_stack[-1] if _policy_stack else _global_policy


def set_precision_policy(policy: PrecisionPolicy) -> None:
    """Set the process-wide default precision policy."""

    global _global_policy
    if not isinstance(policy, PrecisionPolicy):
        raise TypeError("policy must be a PrecisionPolicy instance")
    with _policy_lock:
        _global_policy = policy


@contextmanager
def precision_context(policy: Optional[PrecisionPolicy] = None):
    """Temporarily push a precision policy for nested computations."""

    if policy is None:
        yield
        return

    if not isinstance(policy, PrecisionPolicy):
        raise TypeError("policy must be a PrecisionPolicy instance or None")

    with _policy_lock:
        _policy_stack.append(policy)
    try:
        yield
    finally:
        with _policy_lock:
            _policy_stack.pop()


_env_policy = _load_policy_from_env()
if _env_policy is not None:
    set_precision_policy(_env_policy)
