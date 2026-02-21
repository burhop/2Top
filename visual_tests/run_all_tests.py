"""Interactive runner for visual geometry tests."""

from __future__ import annotations

import argparse
import os
import queue
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from typing import Callable, List, Optional

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    TK_AVAILABLE = True
except Exception:  # pragma: no cover
    TK_AVAILABLE = False


# Ensure parent directory is available for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from visual_tests.utils.plotting import register_embed_viewer


@dataclass
class VisualTestCase:
    name: str
    description: str
    runner: Callable[[], None]


def load_visual_tests() -> List[VisualTestCase]:
    from visual_tests.curve_tests.test_basic_curves import (
        run_all_basic_curve_tests,
    )
    from visual_tests.curve_tests.test_composite_curves import (
        run_all_composite_curve_tests,
    )
    from visual_tests.region_tests.test_basic_regions import (
        run_all_basic_region_tests,
    )
    from visual_tests.comprehensive.test_grid_showcase import (
        run_all_comprehensive_tests,
    )
    from visual_tests.utils.plotting import register_embed_viewer
    from visual_tests.demos.basic_demo import run_basic_demo
    from visual_tests.demos.advanced_demo import run_advanced_demo

    return [
        VisualTestCase("Basic Curves", "Conic sections", run_all_basic_curve_tests),
        VisualTestCase("Composite Curves", "Trimmed/composite curves", run_all_composite_curve_tests),
        VisualTestCase("Regions", "Filled regions & containment", run_all_basic_region_tests),
        VisualTestCase("Grid Showcase", "Comprehensive grid of examples", run_all_comprehensive_tests),
        VisualTestCase("Basic Demo", "Interactive walkthrough", run_basic_demo),
        VisualTestCase("Advanced Demo", "Advanced visualizations", run_advanced_demo),
    ]


def run_tests_cli(tests: List[VisualTestCase], start: int = 0, stop: Optional[int] = None) -> bool:
    stop_index = stop if stop is not None else len(tests)
    all_passed = True
    print("\n" + "=" * 80)
    print("RUNNING VISUAL TESTS")
    print("=" * 80)
    for idx in range(start, min(stop_index, len(tests))):
        case = tests[idx]
        print(f"\n[{idx + 1}/{len(tests)}] {case.name}")
        start_time = time.perf_counter()
        try:
            case.runner()
            elapsed = time.perf_counter() - start_time
            print(f"✓ Completed in {elapsed:.2f}s: {case.description}")
        except Exception as exc:
            all_passed = False
            print(f"✗ {case.name} failed: {exc}")
            traceback.print_exc()
    print("\n" + "=" * 80)
    print("RESULT: " + ("SUCCESS" if all_passed else "FAILURES ENCOUNTERED"))
    print("=" * 80)
    return all_passed


class VisualTestPlayer:
    def __init__(self, root: tk.Tk, tests: List[VisualTestCase]):
        if not TK_AVAILABLE:
            raise RuntimeError("Tkinter is not available on this environment")
        self.root = root
        self.tests = tests
        self.index = 0
        self.playing = False
        self.current_thread: Optional[threading.Thread] = None
        self.queue: "queue.Queue" = queue.Queue()
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.figure_cache: dict[str, plt.Figure] = {}
        register_embed_viewer(self._embed_figure)
        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        self.root.title("Visual Geometry Test Player")
        self.root.geometry("960x640")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(1, weight=1)
        main.rowconfigure(2, weight=1)

        # Test list
        list_frame = ttk.Frame(main)
        list_frame.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=(0, 12))
        ttk.Label(list_frame, text="Tests", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.listbox = tk.Listbox(list_frame, height=20, exportselection=False)
        for case in self.tests:
            self.listbox.insert(tk.END, case.name)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # Detail panel
        detail = ttk.Frame(main)
        detail.grid(row=0, column=1, sticky="ew")
        detail.columnconfigure(0, weight=1)
        self.title_var = tk.StringVar(value="Select a test")
        self.desc_var = tk.StringVar(value="")
        ttk.Label(detail, textvariable=self.title_var, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(detail, textvariable=self.desc_var, font=("Segoe UI", 10), foreground="#666").grid(row=1, column=0, sticky="w")

        # Output/log + canvas
        display_frame = ttk.Frame(main)
        display_frame.grid(row=1, column=1, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=3)
        display_frame.rowconfigure(1, weight=1)

        self.canvas_container = ttk.Frame(display_frame)
        self.canvas_container.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        log_frame = ttk.LabelFrame(display_frame, text="Output")
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log = scrolledtext.ScrolledText(log_frame, height=8, state="disabled")
        self.log.grid(row=0, column=0, sticky="nsew")

        # Controls
        control = ttk.Frame(main)
        control.grid(row=2, column=1, sticky="ew", pady=(12, 0))
        control.columnconfigure(1, weight=1)
        self.prev_btn = ttk.Button(control, text="◀ Previous", command=self.run_previous)
        self.prev_btn.grid(row=0, column=0, padx=4)
        self.play_btn = ttk.Button(control, text="► Play", command=self.toggle_play)
        self.play_btn.grid(row=0, column=1, padx=4)
        self.next_btn = ttk.Button(control, text="Next ▶", command=self.run_next)
        self.next_btn.grid(row=0, column=2, padx=4)
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(control, textvariable=self.status_var).grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self.listbox.selection_set(0)
        self._update_detail()

    def _log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _run_test_thread(self, index: int) -> None:
        case = self.tests[index]
        start = time.perf_counter()
        try:
            case.runner()
            duration = time.perf_counter() - start
            self.queue.put(("result", index, True, duration, None))
        except Exception as exc:  # pragma: no cover - UI reporting only
            duration = time.perf_counter() - start
            self.queue.put(("result", index, False, duration, str(exc)))
            traceback.print_exc()

    def _start_thread(self, index: int) -> None:
        if self.current_thread and self.current_thread.is_alive():
            return
        self._set_status(f"Running: {self.tests[index].name}")
        self.current_thread = threading.Thread(target=self._run_test_thread, args=(index,), daemon=True)
        self.current_thread.start()

    def _on_select(self, event=None) -> None:
        selection = self.listbox.curselection()
        if selection:
            self.index = selection[0]
            self._update_detail()

    def _update_detail(self) -> None:
        case = self.tests[self.index]
        self.title_var.set(case.name)
        self.desc_var.set(case.description)

    def run_current(self) -> None:
        self._start_thread(self.index)

    def run_previous(self) -> None:
        if self.index > 0:
            self.index -= 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.index)
            self._update_detail()
            self.run_current()

    def run_next(self) -> None:
        if self.index < len(self.tests) - 1:
            self.index += 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.index)
            self._update_detail()
            self.run_current()

    def toggle_play(self) -> None:
        self.playing = not self.playing
        self.play_btn.config(text="❚❚ Pause" if self.playing else "► Play")
        if self.playing and not (self.current_thread and self.current_thread.is_alive()):
            self.run_current()

    def _poll_queue(self) -> None:
        try:
            while True:
                message = self.queue.get_nowait()
                if message[0] == "result":
                    _, idx, success, duration, error = message
                    status = "✓" if success else "✗"
                    log_line = f"{status} {self.tests[idx].name} ({duration:.2f}s)"
                    if error:
                        log_line += f" — {error}"
                    self._log(log_line)
                    self._set_status("Idle" if success else f"Failed: {self.tests[idx].name}")
                    if self.playing:
                        if success and idx < len(self.tests) - 1:
                            self.index = idx + 1
                            self.listbox.selection_clear(0, tk.END)
                            self.listbox.selection_set(self.index)
                            self._update_detail()
                            self.run_current()
                        else:
                            self.playing = False
                            self.play_btn.config(text="► Play")
                self.queue.task_done()
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _embed_figure(self, fig) -> None:
        for child in self.canvas_container.winfo_children():
            child.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_container)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        self.canvas = canvas


def run_gui(tests: List[VisualTestCase]) -> int:
    if not TK_AVAILABLE:
        print("Tkinter not available; falling back to CLI mode.")
        return run_tests_cli(tests)
    root = tk.Tk()
    VisualTestPlayer(root, tests)
    root.mainloop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Visual geometry test runner")
    parser.add_argument("--mode", choices=["gui", "cli"], default="gui")
    parser.add_argument("--start", type=int, default=1, help="Start index for CLI mode")
    parser.add_argument("--stop", type=int, default=None, help="Stop index (exclusive) for CLI mode")
    args = parser.parse_args()

    tests = load_visual_tests()
    if args.mode == "gui":
        return run_gui(tests)
    start = max(0, args.start - 1)
    stop = args.stop - 1 if args.stop else None
    return 0 if run_tests_cli(tests, start, stop) else 1


if __name__ == "__main__":
    sys.exit(main())
