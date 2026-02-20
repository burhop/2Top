"""Factories for generating large volumes of geometry regression scenarios.

The intent of this module is to provide deterministic, seed-based generators that can
emit tens of thousands of curve/region/intersection scenarios for fast regression
runs.  The heavy lifting (evaluation, verification, caching) will happen in the
regression harness; this file only focuses on producing structured inputs.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import sympy as sp

from geometry import (
    CompositeCurve,
    ConicSection,
    PrecisionPolicy,
    TrimmedImplicitCurve,
)


@dataclass
class CurveScenario:
    """Container describing a single regression scenario."""

    name: str
    curves: List[TrimmedImplicitCurve]
    composite: Optional[CompositeCurve] = None
    metadata: Dict[str, float] = field(default_factory=dict)

    def descriptor(self) -> Dict[str, float]:
        return {
            "num_segments": len(self.curves),
            "has_composite": float(self.composite is not None),
            **self.metadata,
        }


def _default_precision_policy() -> PrecisionPolicy:
    return PrecisionPolicy()


def _make_quarter_circle(center: Tuple[float, float], radius: float, quadrant: int) -> TrimmedImplicitCurve:
    x, y = sp.symbols("x y")
    circle = ConicSection((x - center[0]) ** 2 + (y - center[1]) ** 2 - radius**2, variables=(x, y))
    mask: Callable[[float, float], bool]

    if quadrant == 0:
        mask = lambda px, py: px >= center[0] and py >= center[1]
    elif quadrant == 1:
        mask = lambda px, py: px <= center[0] and py >= center[1]
    elif quadrant == 2:
        mask = lambda px, py: px <= center[0] and py <= center[1]
    else:
        mask = lambda px, py: px >= center[0] and py <= center[1]

    return TrimmedImplicitCurve(circle, mask)


def generate_quarter_circle_composites(
    seed: int,
    count: int,
    precision_policy: Optional[PrecisionPolicy] = None,
) -> Iterable[CurveScenario]:
    rng = random.Random(seed)
    policy = precision_policy or _default_precision_policy()

    for idx in range(count):
        cx = rng.uniform(-5.0, 5.0)
        cy = rng.uniform(-5.0, 5.0)
        radius = rng.uniform(0.5, 5.0)
        quadrants = [
            _make_quarter_circle((cx, cy), radius, q)
            for q in range(4)
        ]
        composite = CompositeCurve(quadrants, precision_policy=policy)
        yield CurveScenario(
            name=f"quarter-circle-{idx}",
            curves=quadrants,
            composite=composite,
            metadata={"radius": radius},
        )


def sample_scenarios(
    seed: int,
    max_scenarios: int = 100,
    precision_policy: Optional[PrecisionPolicy] = None,
) -> List[CurveScenario]:
    """Return a mixed list of scenarios for smoke/property tests."""

    scenarios: List[CurveScenario] = []
    for scenario in generate_quarter_circle_composites(seed, max_scenarios, precision_policy):
        scenarios.append(scenario)
    return scenarios
