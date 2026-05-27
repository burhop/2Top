"""
Lightweight performance utilities for test timing and regression detection.
"""

import time
import functools
import json
from pathlib import Path

PERF_LOG = (
    Path(__file__).resolve().parent.parent.parent / "test_results" / "perf_log.jsonl"
)


def timed(max_seconds: float = 5.0):
    """Decorator that fails the test if it exceeds max_seconds.
    Also logs timing data to a JSONL file for trend analysis."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start

            PERF_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(PERF_LOG, "a") as f:
                json.dump(
                    {
                        "test": func.__name__,
                        "elapsed_s": round(elapsed, 4),
                        "max_s": max_seconds,
                        "timestamp": time.time(),
                        "passed": elapsed < max_seconds,
                    },
                    f,
                )
                f.write("\n")

            assert elapsed < max_seconds, (
                f"{func.__name__} took {elapsed:.2f}s, limit is {max_seconds}s"
            )
            return result

        return wrapper

    return decorator
