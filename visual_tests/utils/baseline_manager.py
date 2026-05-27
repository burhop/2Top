"""Baseline capture and diff utilities for visual tests."""

from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.image as mpimg
import numpy as np


@dataclass
class BaselineResult:
    status: str
    output_path: Path
    baseline_path: Optional[Path] = None
    diff_path: Optional[Path] = None
    mean_diff: Optional[float] = None
    max_diff: Optional[float] = None


class VisualBaselineManager:
    """Handles saving figures for baseline capture and comparison."""

    def __init__(self) -> None:
        root = Path(__file__).resolve().parent.parent
        self.mode = os.getenv("VISUAL_TEST_MODE", "show").lower()
        self.threshold = float(os.getenv("VISUAL_DIFF_THRESHOLD", "0.01"))
        default_output = root / "output"
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.output_dir = Path(
            os.getenv("VISUAL_OUTPUT_DIR", default_output / timestamp)
        )
        self.baseline_dir = Path(os.getenv("VISUAL_BASELINE_DIR", root / "baselines"))
        self.diff_dir = Path(os.getenv("VISUAL_DIFF_DIR", self.output_dir / "diffs"))
        for directory in [self.output_dir, self.diff_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        if self.mode == "baseline":
            self.baseline_dir.mkdir(parents=True, exist_ok=True)

    def is_active(self) -> bool:
        return self.mode in {"baseline", "compare", "capture"}

    def save_figure(self, fig, name: str, dpi: int = 120) -> BaselineResult:
        filename = f"{name}.png"
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")

        if self.mode == "baseline":
            baseline_path = self.baseline_dir / filename
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(output_path, baseline_path)
            return BaselineResult("baseline_saved", output_path, baseline_path)

        if self.mode == "compare":
            baseline_path = self.baseline_dir / filename
            if not baseline_path.exists():
                raise FileNotFoundError(
                    f"Missing baseline image for {name}. Expected at {baseline_path}"
                )
            baseline = mpimg.imread(baseline_path)
            current = mpimg.imread(output_path)
            if baseline.shape != current.shape:
                raise AssertionError(
                    f"Image shape mismatch for {name}: baseline {baseline.shape} vs current {current.shape}"
                )
            diff = np.abs(current[..., :3] - baseline[..., :3])
            mean_diff = float(diff.mean())
            max_diff = float(diff.max())
            if mean_diff > self.threshold:
                if max_diff > 0:
                    normalized = diff / max_diff
                else:
                    normalized = diff
                diff_path = self.diff_dir / f"{name}_diff.png"
                mpimg.imsave(diff_path, normalized)
                raise AssertionError(
                    f"Visual diff above threshold for {name}: mean={mean_diff:.6f}, max={max_diff:.6f}. "
                    f"See {diff_path}"
                )
            return BaselineResult(
                "matched",
                output_path,
                baseline_path,
                mean_diff=mean_diff,
                max_diff=max_diff,
            )

        # capture mode simply stores the image in output directory
        return BaselineResult("saved", output_path)


_MANAGER: Optional[VisualBaselineManager] = None


def get_baseline_manager() -> VisualBaselineManager:
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = VisualBaselineManager()
    return _MANAGER
