from __future__ import annotations

from typing import Callable, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


def build_buttons_panel(owner, registry: Dict[str, Callable[[], None]]) -> QWidget:
    """Create a vertical buttons panel from a label->handler registry.

    Parameters
    ----------
    owner : QObject-like
        Used only as the parent widget for proper Qt ownership.
    registry : Dict[str, Callable]
        Mapping from button label to slot/callable handler.

    Returns
    -------
    QWidget
        A widget containing a vertical stack of buttons wired to the handlers.
    """
    panel = QWidget(parent=owner)
    layout = QVBoxLayout(panel)
    layout.setAlignment(Qt.AlignTop)
    for label, handler in registry.items():
        btn = QPushButton(label, parent=panel)
        btn.clicked.connect(handler)  # type: ignore[arg-type]
        layout.addWidget(btn)
    layout.addStretch(1)
    return panel
