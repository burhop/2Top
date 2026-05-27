"""Precision-policy fixtures and utilities for geometry tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytest

from geometry import PrecisionPolicy


@dataclass(frozen=True)
class PrecisionProfile:
    name: str
    policy: PrecisionPolicy


DEFAULT_PROFILES: List[PrecisionProfile] = [
    PrecisionProfile(
        "tight", PrecisionPolicy(absolute=1e-7, relative=1e-6, distance_factor=1e-5)
    ),
    PrecisionProfile("default", PrecisionPolicy()),
    PrecisionProfile(
        "loose", PrecisionPolicy(absolute=1e-5, relative=1e-4, distance_factor=5e-4)
    ),
]


@pytest.fixture(params=DEFAULT_PROFILES, ids=lambda prof: prof.name)
def precision_profile(request) -> PrecisionProfile:
    """Iterate through standard precision profiles for parameterized tests."""

    return request.param


def blended_tolerance(profile: PrecisionProfile, scale_hint: float = 1.0) -> float:
    """Helper to compute blended tolerance for assertions."""

    return profile.policy.blended_tolerance(scale_hint)
