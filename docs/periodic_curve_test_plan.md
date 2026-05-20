# Periodic Curve Testing & Fix Plan

Systematic test suite to reproduce and fix periodic curve issues (drawing, endpoint/intersection accuracy, and performance).

## Approach

Work through test cases **one at a time, simplest first**. For each case:
1. Compute the **analytical (expected) solution** by hand / SymPy.
2. Run the solution through the geometry module.
3. Compare results. If **wrong → fix the geometry module** before moving on.
4. Keep the passing case as a **permanent regression test**.
5. Record **timing metrics** for every intersection call.
6. **Update the live status dashboard** after every test case.

> [!IMPORTANT]
> **Timing target: < 0.5 seconds** per intersection search. Any case exceeding this must be investigated and optimized.

---

## Live Status Dashboard

### File Location

```
d:\repos\2Top\docs\periodic_curve_test_status.md
```

This file must be **rewritten after every single test case completes** (not just at the end). The implementing agent must open and overwrite this file each time a test finishes so that it can be watched live in the IDE.

### File Format

The dashboard is a markdown file with the following structure:

````markdown
# Periodic Curve Test Status

> Last updated: 2026-05-20 07:15:32 EST

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 155 |
| ✅ Passed | 12 |
| ❌ Failed / Not run | 140 |
| 🟡 In progress | 1 |
| ⚠️ Passed but slow (> 0.5s) | 2 |
| Avg time (passed) | 0.087s |
| Max time (passed) | 0.342s |

---

## Tier 1 — Periodic + Line (40 cases)

| # | Test | Status | Time | Details |
|---|------|--------|------|---------|
| 1.01 | `sin(x)` ∩ `y=0` | ✅ | 0.045s | 5/5 pts found |
| 1.02 | `sin(x)` ∩ `y=0.5` | ✅ | 0.062s | 4/4 pts found |
| 1.03 | `cos(x)` ∩ `y=0` | 🟡 | — | Running... |
| 1.04 | `sin(x)` ∩ `y=-1` | ❌ | — | Not run |
| 1.05 | `sin(x)` ∩ `y=1.5` (no intersect) | ❌ | — | Not run |
| ... | ... | ... | ... | ... |

## Tier 2 — Periodic + Conic (40 cases)

| # | Test | Status | Time | Details |
|---|------|--------|------|---------|
| 2.01 | `sin(x)` ∩ unit circle | ❌ | — | Not run |
| ... | ... | ... | ... | ... |

## Tier 3 — Periodic + Periodic (40 cases)

| # | Test | Status | Time | Details |
|---|------|--------|------|---------|
| 3.01 | `sin(x)` ∩ `cos(x)` | ❌ | — | Not run |
| ... | ... | ... | ... | ... |

## Tier 4 — Performance / Extended Domain (35 cases)

| # | Test | Status | Time | Details |
|---|------|--------|------|---------|
| 4.01 | `sin(x)` ∩ `y=0` [−10π,10π] | ❌ | — | Not run |
| ... | ... | ... | ... | ... |
````

### Status Icons

| Icon | Meaning | When to use |
|------|---------|-------------|
| ❌ | Not run or failed | Initial state for all tests; also set when a test assertion fails |
| 🟡 | In progress | Set **before** starting a test case; cleared when it finishes |
| ✅ | Passed | Test passed with correct results and timing ≤ 0.5s |
| ⚠️ | Passed but slow | Test results correct but timing > 0.5s |

### Details Column Content

- **Not run:** `Not run`
- **In progress:** `Running...`
- **Passed:** `{found}/{expected} pts found` (e.g. `5/5 pts found`)
- **Passed, zero expected:** `0/0 pts — correct no-intersection`
- **Passed but slow:** `4/4 pts found (SLOW: 0.72s > 0.5s target)`
- **Failed — wrong count:** `Found 3, expected 5 — MISSING 2 pts`
- **Failed — spurious:** `Found 7, expected 5 — 2 SPURIOUS pts`
- **Failed — wrong position:** `5/5 pts but max error 0.15 > tol 0.01`
- **Failed — exception:** `ERROR: ValueError: ...`
- **Failed after fix attempt:** `REGRESSED: was ✅, now fails after fix to X`

### Update Protocol

The implementing agent **must** follow this exact protocol:

1. **Before the very first test:** Create the file with all tests marked ❌.
2. **Before starting each test:** Update that test's row to 🟡 with `Running...`. Write the file.
3. **After each test completes:** Update the row to ✅, ⚠️, or ❌ with details. Update the Summary counters. Write the file.
4. **After a fix is applied:** Re-run all previously-passing tests to check for regressions. Update any that regressed to ❌ with `REGRESSED` note.
5. **File writes must flush immediately** — use `open(path, 'w') as f: f.write(...); f.flush()` to ensure the IDE picks up changes.

### Implementation Notes for the Executing Agent

The simplest approach is a helper class:

```python
class TestDashboard:
    """Manages the live status dashboard markdown file."""
    
    STATUS_PATH = r"d:\repos\2Top\docs\periodic_curve_test_status.md"
    
    def __init__(self):
        self.tests = {}  # test_id -> {name, status, time, details, tier}
        self._init_all_tests()
    
    def _init_all_tests(self):
        """Register all 155+ tests with ❌ status."""
        ...
    
    def mark_running(self, test_id: str):
        """Set test to 🟡 and write file."""
        self.tests[test_id]["status"] = "🟡"
        self.tests[test_id]["details"] = "Running..."
        self._write()
    
    def mark_passed(self, test_id: str, time_s: float, found: int, expected: int):
        """Set test to ✅ or ⚠️ and write file."""
        if time_s > 0.5:
            self.tests[test_id]["status"] = "⚠️"
            self.tests[test_id]["details"] = f"{found}/{expected} pts found (SLOW: {time_s:.3f}s > 0.5s target)"
        else:
            self.tests[test_id]["status"] = "✅"
            self.tests[test_id]["details"] = f"{found}/{expected} pts found"
        self.tests[test_id]["time"] = f"{time_s:.3f}s"
        self._write()
    
    def mark_failed(self, test_id: str, found: int, expected: int, error: str = None):
        """Set test to ❌ with failure details and write file."""
        ...
        self._write()
    
    def _write(self):
        """Rewrite the entire markdown file and flush."""
        lines = self._render_markdown()
        with open(self.STATUS_PATH, 'w', encoding='utf-8') as f:
            f.write(lines)
            f.flush()
    
    def _render_markdown(self) -> str:
        """Generate the full markdown content from current state."""
        ...
```

This class should be instantiated **once** at the start of the test run (not per-test). It can be used either:
- **Inside pytest** via a session-scoped fixture, OR
- **In a standalone script** that runs tests sequentially and updates the dashboard.

A standalone script is preferred since `pytest` parallelism and output capture can interfere with the live-update behavior. The script should:

```python
dashboard = TestDashboard()
for test_id, test_func in ALL_TESTS:
    dashboard.mark_running(test_id)
    try:
        t0 = time.perf_counter()
        found, expected = test_func()
        elapsed = time.perf_counter() - t0
        dashboard.mark_passed(test_id, elapsed, found, expected)
    except AssertionError as e:
        dashboard.mark_failed(test_id, ...)
    except Exception as e:
        dashboard.mark_failed(test_id, error=str(e))
```

The test functions themselves should also be importable by `pytest` for CI/regression use.

---

## Test Tiers

### Tier 1 — Periodic + Line (40 cases)

**Basic sine + horizontal line variations:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.01 | `y - sin(x) = 0` | `y = 0` | [−2π, 2π] | 5 pts: x = kπ |
| 1.02 | `y - sin(x) = 0` | `y = 0.5` | [−2π, 2π] | 4 pts: x = π/6+2kπ, 5π/6+2kπ |
| 1.03 | `y - sin(x) = 0` | `y = 1` | [−2π, 2π] | 2 pts: x = π/2+2kπ (tangent touches) |
| 1.04 | `y - sin(x) = 0` | `y = -1` | [−2π, 2π] | 2 pts: x = −π/2+2kπ |
| 1.05 | `y - sin(x) = 0` | `y = 1.5` | [−2π, 2π] | **0 pts** (no intersection — degenerate) |
| 1.06 | `y - sin(x) = 0` | `y = -0.5` | [−2π, 2π] | 4 pts |
| 1.07 | `y - sin(x) = 0` | `y = sin(1)` ≈ 0.8415 | [−2π, 2π] | 4 pts |

**Cosine + horizontal line:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.08 | `y - cos(x) = 0` | `y = 0` | [−2π, 2π] | 4 pts: x = ±π/2, ±3π/2 |
| 1.09 | `y - cos(x) = 0` | `y = 1` | [−2π, 2π] | 3 pts: x = −2π, 0, 2π (tangent) |
| 1.10 | `y - cos(x) = 0` | `y = -1` | [−2π, 2π] | 2 pts: x = ±π |
| 1.11 | `y - cos(x) = 0` | `y = 0.5` | [−2π, 2π] | 4 pts: x = ±π/3+2kπ |
| 1.12 | `y - cos(x) = 0` | `y = cos(2)` ≈ −0.416 | [−2π, 2π] | 4 pts |

**Phase-shifted periodic curves:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.13 | `y - sin(x - π/4) = 0` | `y = 0` | [−2π, 2π] | 5 pts: x = π/4+kπ |
| 1.14 | `y - sin(x + π/3) = 0` | `y = 0.5` | [−2π, 2π] | 4 pts |
| 1.15 | `y - cos(x - π/2) = 0` | `y = 0` | [−2π, 2π] | equivalent to sin(x), 5 pts |
| 1.16 | `y - sin(x - 1) = 0` | `y = 0` | [−2π, 2π] | 4–5 pts: x = 1+kπ |

**Amplitude-scaled:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.17 | `y - 2·sin(x) = 0` | `y = 0` | [−2π, 2π] | 5 pts (same x as 1.01) |
| 1.18 | `y - 2·sin(x) = 0` | `y = 1.5` | [−2π, 2π] | 4 pts: sin(x) = 0.75 |
| 1.19 | `y - 0.5·sin(x) = 0` | `y = 0.3` | [−2π, 2π] | 4 pts: sin(x) = 0.6 |
| 1.20 | `y - 3·cos(x) = 0` | `y = 2` | [−2π, 2π] | 4 pts: cos(x) = 2/3 |
| 1.21 | `y - 2·sin(x) = 0` | `y = 2` | [−2π, 2π] | 2 pts (tangent at peaks) |
| 1.22 | `y - 2·sin(x) = 0` | `y = 3` | [−2π, 2π] | **0 pts** |

**Frequency-scaled:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.23 | `y - sin(2x) = 0` | `y = 0` | [−2π, 2π] | 9 pts: x = kπ/2 |
| 1.24 | `y - sin(3x) = 0` | `y = 0` | [−2π, 2π] | 13 pts: x = kπ/3 |
| 1.25 | `y - sin(0.5x) = 0` | `y = 0` | [−2π, 2π] | 3 pts: x = −2π, 0, 2π |
| 1.26 | `y - cos(2x) = 0` | `y = 0.5` | [−2π, 2π] | 8 pts: cos(2x) = 0.5 → x = ±π/6+kπ |
| 1.27 | `y - sin(πx) = 0` | `y = 0` | [−3, 3] | 7 pts: x = −3,−2,...,3 |

**Vertical and diagonal lines:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.28 | `y - sin(x) = 0` | `x = π/6` (vertical line) | [−2π, 2π] | 1 pt: (π/6, 0.5) |
| 1.29 | `y - sin(x) = 0` | `x = 0` | [−2π, 2π] | 1 pt: (0, 0) |
| 1.30 | `y - sin(x) = 0` | `y = x` (diagonal) | [−2π, 2π] | 3 pts: (0,0) and ≈(±0.876,±0.876) via numerical |
| 1.31 | `y - sin(x) = 0` | `y = x/π` (shallow diagonal) | [−2π, 2π] | multiple pts |
| 1.32 | `y - cos(x) = 0` | `y = -x` | [−2π, 2π] | numerical — verify count |

**ProceduralCurve variants (same math, different code path):**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.33 | `ProceduralCurve(sin)` | `y = 0` | [−2π, 2π] | same as 1.01 |
| 1.34 | `ProceduralCurve(cos)` | `y = 0` | [−2π, 2π] | same as 1.08 |
| 1.35 | `ProceduralCurve(sin(2x))` | `y = 0` | [−2π, 2π] | same as 1.23 |
| 1.36 | `ProceduralCurve(sin)` | `ProceduralCurve(y=0.5)` | [−2π, 2π] | same as 1.02 |

**Edge / degenerate cases:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 1.37 | `y - sin(x) = 0` | `y = 1 + 1e-10` | [−2π, 2π] | **0 pts** (barely no intersection) |
| 1.38 | `y - sin(x) = 0` | `y = 1 - 1e-6` | [−2π, 2π] | 2 pts (near-tangent) |
| 1.39 | `y - sin(x) = 0` | `y = sin(x)` (identical) | [−2π, 2π] | **overlap** — expect empty or special handling |
| 1.40 | `y - sin(100x) = 0` | `y = 0` | [−1, 1] | ~63 pts (high frequency stress) |

---

### Tier 2 — Periodic + Conic (40 cases)

**Sine + circles:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.01 | `y - sin(x) = 0` | `x² + y² - 1 = 0` (unit circle) | [−5, 5] | 4 pts (numerical) |
| 2.02 | `y - sin(x) = 0` | `x² + y² - 4 = 0` (r=2 circle) | [−5, 5] | 4 pts |
| 2.03 | `y - sin(x) = 0` | `(x−π)² + y² - 1 = 0` (offset circle) | [−2, 8] | 2 or 4 pts |
| 2.04 | `y - sin(x) = 0` | `x² + y² - 0.01 = 0` (tiny circle at origin) | [−1, 1] | 2 pts (near 0,0) |
| 2.05 | `y - sin(x) = 0` | `(x−10)² + y² - 1 = 0` (far-away circle) | [−5, 15] | **0 pts** if range clips, 2 if not |
| 2.06 | `y - cos(x) = 0` | `x² + y² - 1 = 0` | [−5, 5] | 4 pts |
| 2.07 | `y - sin(2x) = 0` | `x² + y² - 1 = 0` | [−5, 5] | more pts (higher freq) |
| 2.08 | `y - 2·sin(x) = 0` | `x² + y² - 4 = 0` | [−5, 5] | pts exist on both +/− arcs |

**Sine + ellipses:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.09 | `y - sin(x) = 0` | `x²/4 + y² - 1 = 0` (ellipse a=2, b=1) | [−5, 5] | 4 pts |
| 2.10 | `y - sin(x) = 0` | `x² + y²/4 - 1 = 0` (tall ellipse) | [−5, 5] | 2 pts (sin bounded by 1) |
| 2.11 | `y - cos(x) = 0` | `x²/9 + y²/4 - 1 = 0` | [−5, 5] | pts where cos meets ellipse |
| 2.12 | `y - sin(x) = 0` | `(x−1)²/4 + y² - 1 = 0` (offset ellipse) | [−5, 5] | numerical |

**Sine + parabolas:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.13 | `y - sin(x) = 0` | `y - x² = 0` | [−5, 5] | 3 pts: (0,0) and 2 near ±0.88 |
| 2.14 | `y - sin(x) = 0` | `y + x² = 0` (downward parabola) | [−5, 5] | 1 pt: (0,0) |
| 2.15 | `y - sin(x) = 0` | `y - x²/4 = 0` (wider parabola) | [−5, 5] | multiple pts |
| 2.16 | `y - cos(x) = 0` | `y - x² + 1 = 0` (shifted parabola) | [−5, 5] | tangent at (0,1) plus others |

**Vertical and angled lines (conic degenerate):**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.17 | `y - sin(x) = 0` | `x - π/4 = 0` | [−2π, 2π] | 1 pt: (π/4, √2/2) |
| 2.18 | `y - sin(x) = 0` | `x - π = 0` | [−2π, 2π] | 1 pt: (π, 0) |
| 2.19 | `y - cos(x) = 0` | `x = 0` | [−2π, 2π] | 1 pt: (0, 1) |
| 2.20 | `y - sin(x) = 0` | `x + y = 0` | [−2π, 2π] | sin(x) = −x → 3 pts |

**Periodic radical forms (y² = g(x)):**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.21 | `y² - sin(x) = 0` | `y = 0.5` | [−2π, 2π] | 4 pts: sin(x) = 0.25 |
| 2.22 | `y² - sin(x) = 0` | `y = 0` | [−2π, 2π] | 5 pts: x = kπ (where sin ≥ 0) |
| 2.23 | `y² - sin(x) = 0` | `y = 1` | [0, 2π] | 1 pt: x = π/2 (tangent to upper branch) |
| 2.24 | `y² - 2·sin(x) = 0` (UI default) | `y = 0` | [−2π, 2π] | 5 pts |
| 2.25 | `y² - 2·sin(x) = 0` | `y = 1` | [−2π, 2π] | 4 pts: sin(x) = 0.5 |
| 2.26 | `y² - 2·sin(x) = 0` | `x² + y² - 1 = 0` | [−5, 5] | numerical |
| 2.27 | `y² - 2·sin(x) = 0` | `x² + y² - 4 = 0` | [−5, 5] | numerical |
| 2.28 | `y² - cos(x) = 0` | `y = 0.5` | [−2π, 2π] | 4 pts: cos(x) = 0.25 |

**Amplitude/frequency combos + conics:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.29 | `y - 3·sin(x) = 0` | `x² + y² - 9 = 0` (r=3) | [−5, 5] | many pts |
| 2.30 | `y - sin(3x) = 0` | `x² + y² - 1 = 0` | [−5, 5] | many pts (high freq) |
| 2.31 | `y² - sin(2x) = 0` | `y = 0.5` | [−2π, 2π] | 8 pts |
| 2.32 | `y² - 3·cos(x) = 0` | `y = 1` | [−2π, 2π] | 4 pts: cos(x) = 1/3 |

**Edge / degenerate:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 2.33 | `y - sin(x) = 0` | `x² + y² - 1e-8 = 0` (near-degenerate circle) | [−1, 1] | 0 or 2 pts (near-tangent at origin) |
| 2.34 | `y² - sin(x) = 0` | `y² - sin(x) = 0` (identical) | [−2π, 2π] | overlap — empty |
| 2.35 | `y - sin(x) = 0` | `y - x² + 1 = 0` where parabola tangent to sine | [−5, 5] | near-tangent case |
| 2.36 | `y² - sin(x) = 0` | `y = -0.5` | [−2π, 2π] | 4 pts: lower branch |
| 2.37 | `y² - sin(x) = 0` | `y = 1.5` | [−2π, 2π] | **0 pts** (beyond range) |
| 2.38 | `y - sin(x) = 0` | hyperbola `x² - y² - 1 = 0` | [−5, 5] | numerical |
| 2.39 | `y - sin(x) = 0` | `x·y - 1 = 0` (rectangular hyperbola) | [−5, 5] | numerical |
| 2.40 | `y² - 2·sin(x) = 0` | `y = x` (diagonal) | [−5, 5] | numerical |

---

### Tier 3 — Periodic + Periodic (40 cases)

**Same-frequency, different phase:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.01 | `y - sin(x) = 0` | `y - cos(x) = 0` | [−2π, 2π] | 4 pts: x = π/4+kπ |
| 3.02 | `y - sin(x) = 0` | `y - sin(x + π/2) = 0` | [−2π, 2π] | same as 3.01 (cos = sin shifted) |
| 3.03 | `y - sin(x) = 0` | `y - sin(x + π) = 0` | [−2π, 2π] | 5 pts: sin(x) = −sin(x) → x = kπ |
| 3.04 | `y - sin(x) = 0` | `y - sin(x + π/4) = 0` | [−2π, 2π] | 4 pts |
| 3.05 | `y - cos(x) = 0` | `y - cos(x + π/3) = 0` | [−2π, 2π] | 4 pts |
| 3.06 | `y - sin(x) = 0` | `y - sin(x + π/6) = 0` | [−2π, 2π] | 4 pts |

**Different frequencies:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.07 | `y - sin(x) = 0` | `y - sin(2x) = 0` | [−2π, 2π] | sin(x)=sin(2x) → analytical |
| 3.08 | `y - sin(x) = 0` | `y - sin(3x) = 0` | [−2π, 2π] | many pts |
| 3.09 | `y - sin(x) = 0` | `y - cos(2x) = 0` | [−2π, 2π] | sin(x)=cos(2x)=1−2sin²(x) |
| 3.10 | `y - cos(x) = 0` | `y - sin(2x) = 0` | [−2π, 2π] | cos(x)=2sin(x)cos(x) |
| 3.11 | `y - sin(2x) = 0` | `y - sin(3x) = 0` | [−2π, 2π] | many pts |
| 3.12 | `y - sin(x) = 0` | `y - sin(x/2) = 0` | [−2π, 2π] | analytical |
| 3.13 | `y - sin(2x) = 0` | `y - cos(3x) = 0` | [−2π, 2π] | many pts |

**Amplitude differences:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.14 | `y - sin(x) = 0` | `y - 2·sin(x) = 0` | [−2π, 2π] | 5 pts: sin(x)=0 → x=kπ |
| 3.15 | `y - sin(x) = 0` | `y - 0.5·sin(x) = 0` | [−2π, 2π] | 5 pts: sin(x)=0 → x=kπ |
| 3.16 | `y - 2·sin(x) = 0` | `y - 3·cos(x) = 0` | [−2π, 2π] | 2sin(x)=3cos(x) → tan(x)=3/2, 4 pts |
| 3.17 | `y - sin(x) = 0` | `y + sin(x) = 0` | [−2π, 2π] | sin(x)=−sin(x)→sin(x)=0, 5 pts |
| 3.18 | `y - sin(x) = 0` | `y + cos(x) = 0` | [−2π, 2π] | sin(x)=−cos(x) → x=−π/4+kπ, 4 pts |

**Periodic radical × periodic radical:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.19 | `y² - sin(x) = 0` | `y² - cos(x) = 0` | [−2π, 2π] | sin(x)=cos(x) → 4 x-values × 2 branches = 8 pts |
| 3.20 | `y² - 2·sin(x) = 0` | `y² - 2·cos(x) = 0` | [−2π, 2π] | same x-values, 8 pts |
| 3.21 | `y² - sin(x) = 0` | `y² - sin(2x) = 0` | [−2π, 2π] | sin(x)=sin(2x), multiple pts × 2 branches |
| 3.22 | `y² - sin(x) = 0` | `y² - 0.5·sin(x) = 0` | [−2π, 2π] | sin(x)=0.5·sin(x) → sin(x)=0, 5 pts × 1 (y=0) = 5 pts |
| 3.23 | `y² - sin(x) = 0` | `(y−1)² - sin(x) = 0` | [−2π, 2π] | y²=(y−1)² → y=0.5, then sin(x)=0.25, 4 pts |

**Mixed symbolic + procedural:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.24 | `ImplicitCurve(sin)` | `ProceduralCurve(cos)` | [−2π, 2π] | same as 3.01 |
| 3.25 | `ProceduralCurve(sin)` | `ProceduralCurve(cos)` | [−2π, 2π] | same as 3.01 |
| 3.26 | `ProceduralCurve(sin)` | `ProceduralCurve(sin(2x))` | [−2π, 2π] | same as 3.07 |

**Compound/exotic periodic forms:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.27 | `y - sin(x)·cos(x) = 0` (= sin(2x)/2) | `y = 0` | [−2π, 2π] | 9 pts: x = kπ/2 |
| 3.28 | `y - sin²(x) = 0` | `y = 0.5` | [−2π, 2π] | 8 pts: sin²(x)=0.5 → sin(x)=±√2/2 |
| 3.29 | `y - (sin(x)+cos(x)) = 0` | `y = 0` | [−2π, 2π] | 4 pts: sin(x)=−cos(x) → x = −π/4+kπ |
| 3.30 | `y - sin(x)·cos(x) = 0` | `y - sin(x) = 0` | [−2π, 2π] | sin(x)·cos(x)=sin(x) → sin(x)(cos(x)−1)=0 |
| 3.31 | `y - |sin(x)| = 0` (ProceduralCurve) | `y = 0.5` | [−2π, 2π] | 8 pts |
| 3.32 | `y - sin(x²) = 0` (non-periodic!) | `y = 0` | [−3, 3] | x = 0, ±√π, ±√(2π), ... |

**Degenerate / edge periodic×periodic:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 3.33 | `y - sin(x) = 0` | `y - sin(x) = 0` (identical) | [−2π, 2π] | **overlap** → empty |
| 3.34 | `y - sin(x) = 0` | `y - sin(x) - 1e-10 = 0` (near-identical) | [−2π, 2π] | **0 pts** (parallel offset) |
| 3.35 | `y - sin(x) = 0` | `y - sin(x+1e-8) = 0` (near-identical phase) | [−2π, 2π] | near-overlap — test robustness |
| 3.36 | `y² - sin(x) = 0` | `y = 0` at domain boundary | [0, π] | 2 pts: x = 0, π |
| 3.37 | `y - sin(x) = 0` | `y - cos(x) = 0` at narrow domain | [0, π/2] | 1 pt: x = π/4 |
| 3.38 | `y - sin(x) = 0` | `y - cos(x) = 0` | [π/4, π/4] | degenerate single-point domain |
| 3.39 | `y - sin(1/x) = 0` (Proc.) | `y = 0` | [0.01, 1] | many pts (accumulation near 0) |
| 3.40 | `y - x·sin(1/x) = 0` (Proc.) | `y = 0` | [−1, 1] | many pts near 0 |

---

### Tier 4 — Extended Domain / Performance Stress (35 cases)

**Scaling intersection count:**

| # | Curve A | Curve B | Domain | Expected count | Notes |
|---|---------|---------|--------|----------------|-------|
| 4.01 | `y - sin(x) = 0` | `y = 0` | [−10π, 10π] | 21 pts | baseline |
| 4.02 | `y - sin(x) = 0` | `y = 0` | [−50π, 50π] | 101 pts | stress |
| 4.03 | `y - sin(x) = 0` | `y = 0` | [−100, 100] | 64 pts | non-aligned |
| 4.04 | `y - sin(x) = 0` | `y = 0.5` | [−100, 100] | 64 pts | |
| 4.05 | `y - sin(2x) = 0` | `y = 0` | [−100, 100] | 128 pts | double freq |
| 4.06 | `y - sin(10x) = 0` | `y = 0` | [−10, 10] | 64 pts | high freq, small domain |
| 4.07 | `y - sin(x) = 0` | `y - cos(x) = 0` | [−100, 100] | 64 pts | |

**Periodic radical at scale:**

| # | Curve A | Curve B | Domain | Expected |
|---|---------|---------|--------|----------|
| 4.08 | `y² - 2·sin(x) = 0` | `y = 0` | [−20, 20] | ~13 pts |
| 4.09 | `y² - 2·sin(x) = 0` | `y = 1` | [−20, 20] | ~12 pts |
| 4.10 | `y² - 2·sin(x) = 0` | `x² + y² - 4 = 0` | [−20, 20] | numerical |
| 4.11 | `y² - sin(x) = 0` | `y² - cos(x) = 0` | [−20, 20] | many pts |
| 4.12 | `y² - 2·sin(x) = 0` | `y² - 2·cos(x) = 0` | [−20, 20] | many pts |

**ProceduralCurve at scale (perf-critical):**

| # | Curve A | Curve B | Domain | Expected | Notes |
|---|---------|---------|--------|----------|-------|
| 4.13 | `Proc(sin)` | `y = 0` | [−100, 100] | 64 pts | perf baseline |
| 4.14 | `Proc(sin)` | `Proc(cos)` | [−100, 100] | 64 pts | worst case |
| 4.15 | `Proc(sin)` | `Proc(y=0)` | [−50, 50] | 32 pts | medium |
| 4.16 | `Proc(sin(2x))` | `y = 0` | [−50, 50] | 64 pts | |

**Grid resolution sensitivity:**

| # | Curve A | Curve B | grid_res | Domain | Purpose |
|---|---------|---------|----------|--------|---------|
| 4.17 | `y - sin(x)` | `y = 0` | 100 | [−2π, 2π] | low res accuracy |
| 4.18 | `y - sin(x)` | `y = 0` | 200 | [−2π, 2π] | medium res |
| 4.19 | `y - sin(x)` | `y = 0` | 500 | [−2π, 2π] | default res |
| 4.20 | `y - sin(x)` | `y = 0` | 1000 | [−2π, 2π] | high res |
| 4.21 | `y - sin(10x)` | `y = 0` | 100 | [−2π, 2π] | high freq + low res (likely fails) |
| 4.22 | `y - sin(10x)` | `y = 0` | 500 | [−2π, 2π] | high freq + default res |
| 4.23 | `y - sin(10x)` | `y = 0` | 2000 | [−2π, 2π] | high freq + high res |

**Timing-specific tests:**

| # | Description | Purpose |
|---|-------------|---------|
| 4.24 | Symbolic sine ∩ line, measure 10 runs | avg timing, variance |
| 4.25 | Procedural sine ∩ line, measure 10 runs | compare to 4.24 |
| 4.26 | Symbolic sine ∩ circle, measure 10 runs | conic intersection timing |
| 4.27 | Symbolic sine ∩ sine, measure 10 runs | periodic×periodic timing |
| 4.28 | `y² - 2·sin(x) ∩ circle`, measure 10 runs | radical timing |

**Search range sensitivity:**

| # | Curve A | Curve B | search_range | Domain context | Purpose |
|---|---------|---------|-------------|----------------|---------|
| 4.29 | `y - sin(x)` | `y = 0` | 2.0 | curves span [−2π, 2π] | under-sized range |
| 4.30 | `y - sin(x)` | `y = 0` | 5.0 | curves span [−2π, 2π] | barely adequate |
| 4.31 | `y - sin(x)` | `y = 0` | 10.0 | curves span [−2π, 2π] | adequate |
| 4.32 | `y - sin(x)` | `y = 0` | 50.0 | curves span [−2π, 2π] | over-sized range |

**Large-scale endpoint verification:**

| # | Curve | Domain | Expected endpoint count |
|---|-------|--------|------------------------|
| 4.33 | `y² - 2·sin(x) = 0` | [−100, 100] | ~64 endpoints |
| 4.34 | `y² - 2·sin(x) = 0` | [−1000, 1000] | ~637 endpoints |
| 4.35 | `y² - 2·cos(x) = 0` | [−100, 100] | ~64 endpoints |

---

## Performance Strategy

The 0.5s target requires optimization of the current approach. Key changes:

### 1. ProceduralCurve vectorization
Replace the point-by-point loop in `ProceduralCurve.evaluate()` with `np.vectorize` or `np.frompyfunc`:
```python
# Current: O(N) Python loop
for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
    flat_result[i] = self.function(float(xi), float(yi))

# Proposed: vectorized
vfunc = np.vectorize(self.function)
result = vfunc(x_arr, y_arr)
```

### 2. Adaptive grid resolution
For `find_curve_intersections`, scale grid resolution based on domain size and curve frequency:
- Small domain (< 10): 200–300 grid
- Medium domain (10–50): 400–600 grid  
- Large domain (> 50): Use multi-pass — coarse grid to find regions, then fine grid per region

### 3. Smart search range
Auto-compute `search_range` from curve bounding boxes instead of using a fixed default.

### 4. Reduce clustering overhead
The `pdist` + `linkage` clustering is O(N²). For periodic curves with many candidates, use a faster grid-based deduplication.

---

## Files

### [NEW] [test_periodic_curves.py](file:///d:/repos/2Top/tests/test_periodic_curves.py)

155+ test cases with `@pytest.mark.tier1` through `@pytest.mark.tier4`. The test file should contain both:
- **pytest-compatible test functions** for CI/regression use
- **A `TestDashboard` class** that writes the live status file

### [NEW] [periodic_curve_test_status.md](file:///d:/repos/2Top/docs/periodic_curve_test_status.md)

The live dashboard file. Created automatically by the test harness. See "Live Status Dashboard" section above for exact format.

### [MODIFY] [periodic_curve_test_plan.md](file:///d:/repos/2Top/docs/periodic_curve_test_plan.md)

Update with this final plan content.

### [MODIFY] [curve_intersections.py](file:///d:/repos/2Top/geometry/curve_intersections.py)

Performance and correctness fixes discovered during testing.

### [MODIFY] [implicit_curve.py](file:///d:/repos/2Top/geometry/implicit_curve.py)

Endpoint calculation fixes if tests reveal bugs.

### [MODIFY] [procedural_curve.py](file:///d:/repos/2Top/geometry/procedural_curve.py)

Vectorize `evaluate()` for performance.

---

## Execution Order

1. Create `tests/test_periodic_curves.py` with all tiers and the `TestDashboard` class.
2. Create initial `docs/periodic_curve_test_status.md` with all tests marked ❌.
3. Run Tier 1.01. If it fails → fix the geometry module. Dashboard shows 🟡 then ✅ or ❌.
4. Continue through 1.01–1.40, fixing as needed, dashboard updating live.
5. Tier 2.01–2.40.
6. Tier 3.01–3.40.
7. Tier 4.01–4.35.
8. After all tiers pass, verify final timing summary in dashboard.
9. Update `docs/periodic_curve_test_plan.md` with final results.

## Verification

```bash
# All tests (pytest mode — dashboard also updates)
python -m pytest tests/test_periodic_curves.py -v --tb=short

# Specific tier
python -m pytest tests/test_periodic_curves.py -v -k "tier1"

# Specific case
python -m pytest tests/test_periodic_curves.py -v -k "test_1_01"

# Standalone runner with live dashboard (preferred for watching progress)
python tests/test_periodic_curves.py --run-all
```
