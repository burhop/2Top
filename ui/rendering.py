from __future__ import annotations

import io
import contextlib
import logging
import os
import tempfile
import traceback
from typing import Tuple

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from .view_state import Viewport

# Local logger for rendering module
LOG_PATH = os.path.join(tempfile.gettempdir(), "2top_ui.log")

def get_logger() -> logging.Logger:
    logger = logging.getLogger("2top_ui")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


def render_scene_to_png(scene, filename: str, viewport: Viewport, figsize: Tuple[int, int] = (8, 6), dpi: int = 100) -> None:
    """
    Render the given scene to a PNG file using matplotlib.

    - Uses viewport.xlim/ylim for axes limits
    - Captures stdout/stderr to log
    - Renders objects with graceful per-object error handling
    - If an object appears composite-like (has member_ids), draws members individually
    """
    logger = get_logger()
    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.set_xlim(*viewport.xlim)
        ax.set_ylim(*viewport.ylim)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

        for obj_id in scene.list_objects():
            obj = scene.get_object(obj_id)
            style = scene.get_style(obj_id)
            if hasattr(obj, "plot"):
                # Composite-like detection without depending on concrete class
                member_ids = getattr(obj, "member_ids", None)
                if isinstance(member_ids, (list, tuple)):
                    alpha = style.get("alpha", 1.0)
                    for mid in member_ids:
                        try:
                            mobj = scene.get_object(mid)
                            mstyle = scene.get_style(mid).copy()
                            mstyle["alpha"] = min(alpha, mstyle.get("alpha", 1.0)) * 0.9
                            if hasattr(mobj, "plot"):
                                mobj.plot(xlim=viewport.xlim, ylim=viewport.ylim, ax=ax, **mstyle)
                        except Exception:
                            logger.error(
                                "Render error for composite member %s (from %s):\n%s",
                                mid,
                                obj_id,
                                traceback.format_exc(),
                            )
                            continue
                else:
                    try:
                        obj.plot(xlim=viewport.xlim, ylim=viewport.ylim, ax=ax, **style)
                    except Exception:
                        logger.error(
                            "Render error for object %s (%s):\n%s",
                            obj_id,
                            type(obj).__name__,
                            traceback.format_exc(),
                        )
                        continue

        plt.tight_layout()
        fig.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    out = stdout_buf.getvalue()
    err = stderr_buf.getvalue()
    if out.strip():
        logger.debug("STDOUT during render:\n%s", out)
    if err.strip():
        logger.warning("STDERR during render:\n%s", err)
