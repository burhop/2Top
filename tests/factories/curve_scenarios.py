"""Factories for generating large volumes of geometry regression scenarios.

The intent of this module is to provide deterministic, seed-based generators that can
emit tens of thousands of curve/region/intersection scenarios for fast regression
runs.  The heavy lifting (evaluation, verification, caching) will happen in the
regression harness; this file only focuses on producing structured inputs.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import sympy as sp

from geometry import (
    CompositeCurve,
    ConicSection,
    PrecisionPolicy,
    TrimmedImplicitCurve,
)
from geometry.polynomial_curve import PolynomialCurve


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


def _make_quarter_circle(
    center: Tuple[float, float], radius: float, quadrant: int
) -> TrimmedImplicitCurve:
    x, y = sp.symbols("x y")
    circle = ConicSection(
        (x - center[0]) ** 2 + (y - center[1]) ** 2 - radius**2, variables=(x, y)
    )
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
        quadrants = [_make_quarter_circle((cx, cy), radius, q) for q in range(4)]
        composite = CompositeCurve(quadrants, precision_policy=policy)
        yield CurveScenario(
            name=f"quarter-circle-{idx}",
            curves=quadrants,
            composite=composite,
            metadata={"radius": radius},
        )


def _make_line_segment(
    point_a: Tuple[float, float], point_b: Tuple[float, float]
) -> TrimmedImplicitCurve:
    x, y = sp.symbols("x y")
    ax, ay = point_a
    bx, by = point_b

    if abs(ax - bx) < 1e-9:
        line = PolynomialCurve(x - ax, variables=(x, y))
        return TrimmedImplicitCurve(
            line,
            lambda px, py, _ay=ay, _by=by: min(_ay, _by) <= py <= max(_ay, _by),
            xmin=min(ax, bx),
            xmax=max(ax, bx),
            ymin=min(ay, by),
            ymax=max(ay, by),
            endpoints=[point_a, point_b],
        )
    else:
        slope = (by - ay) / (bx - ax)
        intercept = ay - slope * ax
        line = PolynomialCurve(y - (slope * x + intercept), variables=(x, y))
        return TrimmedImplicitCurve(
            line,
            lambda px, py, _ax=ax, _bx=bx: min(_ax, _bx) <= px <= max(_ax, _bx),
            xmin=min(ax, bx),
            xmax=max(ax, bx),
            ymin=min(ay, by),
            ymax=max(ay, by),
            endpoints=[point_a, point_b],
        )


def generate_axis_aligned_rectangles(
    seed: int,
    count: int,
    precision_policy: Optional[PrecisionPolicy] = None,
) -> Iterable[CurveScenario]:
    rng = random.Random(seed)
    policy = precision_policy or _default_precision_policy()

    for idx in range(count):
        min_x = rng.uniform(-5, 4)
        min_y = rng.uniform(-5, 4)
        width = rng.uniform(0.5, 3)
        height = rng.uniform(0.5, 3)
        max_x = min_x + width
        max_y = min_y + height
        points = [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
        ]
        segments = [
            _make_line_segment(points[i], points[(i + 1) % 4]) for i in range(4)
        ]
        composite = CompositeCurve(segments, precision_policy=policy)
        yield CurveScenario(
            name=f"rectangle-{idx}",
            curves=segments,
            composite=composite,
            metadata={"width": width, "height": height},
        )


def generate_random_open_polylines(
    seed: int,
    count: int,
    precision_policy: Optional[PrecisionPolicy] = None,
) -> Iterable[CurveScenario]:
    rng = random.Random(seed)
    policy = precision_policy or _default_precision_policy()

    for idx in range(count):
        num_segments = rng.randint(2, 5)
        points = [(rng.uniform(-3, 3), rng.uniform(-3, 3))]
        for _ in range(num_segments):
            dx = rng.uniform(-1.5, 1.5)
            dy = rng.uniform(-1.5, 1.5)
            last_x, last_y = points[-1]
            points.append((last_x + dx, last_y + dy))
        segments = [
            _make_line_segment(points[i], points[i + 1]) for i in range(len(points) - 1)
        ]
        composite = CompositeCurve(segments, precision_policy=policy)
        yield CurveScenario(
            name=f"polyline-{idx}",
            curves=segments,
            composite=composite,
            metadata={
                "num_segments": len(segments),
                "closed": float(composite.is_closed()),
            },
        )


def sample_scenarios(
    seed: int,
    max_scenarios: int = 100,
    precision_policy: Optional[PrecisionPolicy] = None,
) -> List[CurveScenario]:
    """Return a mixed list of scenarios for smoke/property tests."""

    batches = max(1, max_scenarios // 3)
    scenarios: List[CurveScenario] = []
    generators = [
        generate_quarter_circle_composites,
        generate_axis_aligned_rectangles,
        generate_random_open_polylines,
    ]
    for offset, generator in enumerate(generators):
        for scenario in generator(seed + offset * 101, batches, precision_policy):
            scenarios.append(scenario)
            if len(scenarios) >= max_scenarios:
                return scenarios
    return scenarios
