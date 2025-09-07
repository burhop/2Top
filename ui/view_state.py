from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class Viewport:
    xlim: Tuple[float, float] = (-5.0, 5.0)
    ylim: Tuple[float, float] = (-5.0, 5.0)

    def apply(self, xmin: float, xmax: float, ymin: float, ymax: float, pad_ratio: float = 0.02) -> None:
        vals = np.array([xmin, xmax, ymin, ymax], dtype=float)
        if not np.isfinite(vals).all():
            return
        if xmax == xmin:
            xmin -= 0.5
            xmax += 0.5
        if ymax == ymin:
            ymin -= 0.5
            ymax += 0.5
        dx = xmax - xmin
        dy = ymax - ymin
        xmin -= dx * pad_ratio
        xmax += dx * pad_ratio
        ymin -= dy * pad_ratio
        ymax += dy * pad_ratio
        self.xlim = (float(xmin), float(xmax))
        self.ylim = (float(ymin), float(ymax))

    def set_limits(self, xlim: Tuple[float, float], ylim: Tuple[float, float]) -> None:
        self.xlim = (float(xlim[0]), float(xlim[1]))
        self.ylim = (float(ylim[0]), float(ylim[1]))

    def zoom_in(self, factor: float = 0.8) -> None:
        cx = (self.xlim[0] + self.xlim[1]) * 0.5
        cy = (self.ylim[0] + self.ylim[1]) * 0.5
        dx = (self.xlim[1] - self.xlim[0]) * 0.5 * factor
        dy = (self.ylim[1] - self.ylim[0]) * 0.5 * factor
        self.apply(cx - dx, cx + dx, cy - dy, cy + dy, pad_ratio=0.0)

    def zoom_out(self, factor: float = 1 / 0.8) -> None:
        cx = (self.xlim[0] + self.xlim[1]) * 0.5
        cy = (self.ylim[0] + self.ylim[1]) * 0.5
        dx = (self.xlim[1] - self.xlim[0]) * 0.5 * factor
        dy = (self.ylim[1] - self.ylim[0]) * 0.5 * factor
        self.apply(cx - dx, cx + dx, cy - dy, cy + dy, pad_ratio=0.0)

    def pan(self, frac_x: float, frac_y: float) -> None:
        xmin, xmax = self.xlim
        ymin, ymax = self.ylim
        dx = (xmax - xmin)
        dy = (ymax - ymin)
        shift_x = dx * float(frac_x)
        shift_y = dy * float(frac_y)
        self.apply(xmin + shift_x, xmax + shift_x, ymin + shift_y, ymax + shift_y, pad_ratio=0.0)

    def fit_to_scene(self, scene, pad_ratio: float = 0.05) -> bool:
        # Aggregate bounds across all objects exposing bounding_box()
        xmin = ymin = np.inf
        xmax = ymax = -np.inf
        any_bounds = False
        for oid in scene.list_objects():
            obj = scene.get_object(oid)
            bb = getattr(obj, "bounding_box", None)
            if callable(bb):
                try:
                    b = bb()
                except Exception:
                    b = None
                if b is None:
                    continue
                bxmin, bxmax, bymin, bymax = b
                vals = np.array([bxmin, bxmax, bymin, bymax], dtype=float)
                if not np.isfinite(vals).all():
                    continue
                xmin = min(xmin, bxmin)
                xmax = max(xmax, bxmax)
                ymin = min(ymin, bymin)
                ymax = max(ymax, bymax)
                any_bounds = True
        if any_bounds:
            self.apply(xmin, xmax, ymin, ymax, pad_ratio=pad_ratio)
            return True
        return False
