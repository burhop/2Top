from __future__ import annotations

from typing import Dict, List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
)


class ParameterDialog(QDialog):
    """
    Generic parameter input dialog supporting str, float, int, and bool.

    schema: list[dict] where each dict has keys:
      - name: parameter name (used as kwargs key)
      - label: user-facing label
      - type: one of 'str', 'float', 'int', 'bool'
      - default: default value
      - min, max, step: optional (for numeric types)
    """

    def __init__(self, title: str, schema: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self._schema = schema
        self._inputs: Dict[str, object] = {}

        vbox = QVBoxLayout(self)
        form = QFormLayout()

        for field in schema:
            name = field["name"]
            label = field.get("label", name)
            ftype = field.get("type", "str")
            default = field.get("default")

            if ftype == "float":
                w = QDoubleSpinBox()
                w.setDecimals(6)
                w.setRange(float(field.get("min", -1e9)), float(field.get("max", 1e9)))
                w.setSingleStep(float(field.get("step", 0.1)))
                try:
                    w.setValue(float(default) if default is not None else 0.0)
                except Exception:
                    w.setValue(0.0)
            elif ftype == "int":
                w = QSpinBox()
                w.setRange(int(field.get("min", -10**9)), int(field.get("max", 10**9)))
                w.setSingleStep(int(field.get("step", 1)))
                try:
                    w.setValue(int(default) if default is not None else 0)
                except Exception:
                    w.setValue(0)
            elif ftype == "bool":
                w = QCheckBox()
                w.setChecked(bool(default))
            else:  # str
                w = QLineEdit()
                w.setText(str(default) if default is not None else "")

            self._inputs[name] = w
            form.addRow(label, w)

        vbox.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vbox.addWidget(buttons)

    def values(self) -> Dict[str, object]:
        out: Dict[str, object] = {}
        for name, w in self._inputs.items():
            if isinstance(w, QDoubleSpinBox):
                out[name] = float(w.value())
            elif isinstance(w, QSpinBox):
                out[name] = int(w.value())
            elif isinstance(w, QCheckBox):
                out[name] = bool(w.isChecked())
            elif isinstance(w, QLineEdit):
                out[name] = w.text()
            else:
                # Fallback: try to get .text() or .value()
                val = getattr(w, "value", lambda: None)()
                if val is None:
                    val = getattr(w, "text", lambda: "")()
                out[name] = val
        return out


class ObjectSelectorDialog(QDialog):
    def __init__(self, title: str, items: List[Tuple[str, str]], multi: bool = True, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.selected_ids: List[str] = []
        vbox = QVBoxLayout(self)
        self.listw = QListWidget()
        self.listw.setSelectionMode(QListWidget.MultiSelection if multi else QListWidget.SingleSelection)
        for obj_id, label in items:
            it = QListWidgetItem(f"{obj_id} — {label}")
            it.setData(Qt.UserRole, obj_id)
            self.listw.addItem(it)
        vbox.addWidget(self.listw)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vbox.addWidget(buttons)

    def values(self) -> List[str]:
        out: List[str] = []
        for it in self.listw.selectedItems():
            oid = it.data(Qt.UserRole)
            if isinstance(oid, str):
                out.append(oid)
        return out
