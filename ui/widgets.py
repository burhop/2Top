from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from .view_state import Viewport


class ImageView(QLabel):
    """Interactive image view.

    - Wheel to zoom in/out using the provided Viewport
    - Drag (left mouse) to pan
    - Calls on_viewport_changed() after interactions so caller can re-render
    - Optionally reports mouse world coordinates via on_mouse_move(x, y)
    """

    def __init__(self, viewport: Viewport, on_viewport_changed: Callable[[], None], on_mouse_move: Optional[Callable[[float, float], None]] = None, parent=None):
        super().__init__(parent)
        self._viewport = viewport
        self._on_change = on_viewport_changed
        self._on_mouse_move = on_mouse_move
        self._dragging = False
        self._last_pos: Optional[QPoint] = None
        self.setAlignment(Qt.AlignCenter)
        # Receive mouse move events even when no button is pressed
        self.setMouseTracking(True)

    def set_pixmap(self, pix: QPixmap) -> None:
        # Convenience wrapper for callers
        self.setPixmap(pix)
        if not pix.isNull():
            self.setMinimumSize(pix.width(), pix.height())

    def _pixel_to_world(self, px: int, py: int) -> tuple[float, float]:
        """Map widget pixel coords to world coords using current viewport.

        Assumes the pixmap fills the label area proportionally; we approximate
        mapping linearly across the widget dimensions which is sufficient for
        status readout.
        """
        w = max(1, self.width())
        h = max(1, self.height())
        fx = float(px) / float(w)
        fy = float(py) / float(h)
        xmin, xmax = self._viewport.xlim
        ymin, ymax = self._viewport.ylim
        # Qt y increases downward; world y increases upward
        xw = xmin + fx * (xmax - xmin)
        yw = ymax - fy * (ymax - ymin)
        return xw, yw

    # --- Events ---
    def wheelEvent(self, event):  # type: ignore[override]
        delta = event.angleDelta().y()
        if delta > 0:
            self._viewport.zoom_in()
        elif delta < 0:
            self._viewport.zoom_out()
        self._on_change()
        event.accept()

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # type: ignore[override]
        # Always report mouse position if requested
        if self._on_mouse_move is not None:
            xw, yw = self._pixel_to_world(event.position().x(), event.position().y())  # type: ignore[attr-defined]
            self._on_mouse_move(xw, yw)
        if self._dragging and self._last_pos is not None:
            cur = event.pos()
            dx = cur.x() - self._last_pos.x()
            dy = cur.y() - self._last_pos.y()
            w = max(1, self.width())
            h = max(1, self.height())
            # Drag right moves content right -> pan viewport left (negative frac)
            frac_x = -float(dx) / float(w)
            # Drag down moves content down -> pan viewport up (negative y), but Qt y+ is down
            frac_y = float(dy) / float(h)
            self._viewport.pan(frac_x, frac_y)
            self._last_pos = cur
            self._on_change()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self._last_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
