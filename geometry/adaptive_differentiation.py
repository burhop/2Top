"""Bounded sample-based step selection; estimates are never certified bounds."""

import numpy as np

EPS = np.finfo(float).eps
FLOOR = np.nextafter(0.0, 1.0)
MAX_CANDIDATES = 20


def _stencil(evaluate, x, y, axis, step, center):
    coordinate = (x, y)[axis]
    with np.errstate(all="ignore"):
        plus, minus = coordinate + step, coordinate - step
        plus = np.where(plus == coordinate, np.nextafter(coordinate, np.inf), plus)
        minus = np.where(minus == coordinate, np.nextafter(coordinate, -np.inf), minus)
        hp, hm = plus - coordinate, coordinate - minus
    fp = evaluate(plus, y) if axis == 0 else evaluate(x, plus)
    fm = evaluate(minus, y) if axis == 0 else evaluate(x, minus)
    with np.errstate(all="ignore"):
        forward, backward = (fp - center) / hp, (center - fm) / hm
        wp, wm = hm / (hp + hm), hp / (hp + hm)
        slope = wp * forward + wm * backward
        ep, em, ec = (np.maximum(EPS * np.abs(v), FLOOR) for v in (fp, fm, center))
        rounding = wp * (ep + ec) / hp + wm * (em + ec) / hm
        valid = (
            np.isfinite(plus)
            & np.isfinite(minus)
            & np.isfinite(slope)
            & (hp > 0)
            & (hm > 0)
        )
        return dict(
            slope=slope,
            rounding=rounding,
            gap=np.abs(forward - backward),
            signal=np.maximum(np.abs(fp - center), np.abs(fm - center)),
            steps=(hp, hm),
            valid=valid,
        )


def _candidate(evaluate, x, y, axis, step, center):
    coarse = _stencil(evaluate, x, y, axis, step, center)
    fine = _stencil(evaluate, x, y, axis, step * 0.5, center)
    with np.errstate(all="ignore"):
        ratio = (coarse["steps"][0] / fine["steps"][0]) * (
            coarse["steps"][1] / fine["steps"][1]
        )
        correction = (fine["slope"] - coarse["slope"]) / (ratio - 1)
        extrapolated = fine["slope"] + correction
        valid = (
            coarse["valid"] & fine["valid"] & (ratio > 1.5) & np.isfinite(extrapolated)
        )
        value = np.where(valid, extrapolated, fine["slope"])
        rounding = coarse["rounding"] + fine["rounding"]
        spacing = np.maximum(np.abs(np.spacing(value)), FLOOR)
        error = np.maximum(np.abs(correction) + rounding, spacing)
        sides = fine["gap"] <= 0.8 * coarse["gap"] + 8 * rounding
        signal = np.maximum(coarse["signal"], fine["signal"])
        flat = signal == 0
        stationary = (np.abs(value) <= np.abs(correction) + 8 * spacing) & (
            (signal > 8 * np.maximum(EPS * np.abs(center), FLOOR)) | (center == 0)
        )
        target = (
            (np.abs(correction) <= 1e-6 * np.abs(value))
            & (rounding <= 1e-9 * np.abs(value))
            & (spacing <= 1e-9 * np.abs(value))
        )
        # Flat samples cannot prove a zero component. Retain the finite
        # quantization uncertainty so normal() can compare it with other axes;
        # rejecting every flat axis would reject perfectly regular affine fields.
        eligible = valid & sides & (target | stationary | flat)
        score = error / np.maximum(np.abs(value), np.abs(fine["slope"]))
    return dict(
        value=value,
        error=error,
        rounding=rounding,
        truncation=np.abs(correction),
        eligible=eligible,
        stationary=stationary,
        flat=flat,
        sides=sides,
        score=score,
        valid=valid,
        collapsed=coarse["valid"] & fine["valid"] & (ratio <= 1.5),
        steps=(coarse["steps"], fine["steps"]),
    )


def automatic_gradient(evaluate, x, y, *, diagnostics=True):
    """Per-axis/per-point adaptation with at most 321 vector evaluations.

    Off-ladder and shrinking one-sided agreement reduce common alias/cusp
    failures. A finite set of samples cannot exclude hidden features or noise.
    Callback exceptions propagate; numpy nonfinite probes can be refined.
    """
    evaluations = 0

    def sample(a, b):
        nonlocal evaluations
        evaluations += 1
        return evaluate(a, b)

    center = sample(x, y)
    gradients, errors, steps, statuses, iterations, nominal_steps, selections = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for axis, coordinate in enumerate((x, y)):
        with np.errstate(all="ignore"):
            anchor = np.maximum(EPS**0.2, 8 * np.abs(np.spacing(coordinate)))
        step = anchor.copy()
        done = np.zeros(x.shape, dtype=bool)
        active = np.ones(x.shape, dtype=bool)
        count = np.zeros(x.shape, dtype=int) if diagnostics else None
        value = np.full(x.shape, np.nan)
        error = np.full(x.shape, np.inf) if diagnostics else None
        best_score = np.full(x.shape, np.inf)
        chosen_step = anchor.copy() if diagnostics else None
        chosen_steps = (
            tuple(tuple(np.full(x.shape, np.nan) for _ in range(2)) for _ in range(2))
            if diagnostics
            else None
        )
        status = (
            np.full(x.shape, "budget_exhausted", dtype="<U24") if diagnostics else None
        )
        direction = None
        previous = None
        for _ in range(MAX_CANDIDATES):
            if not np.any(active):
                break
            if diagnostics:
                count = np.where(active, count + 1, count)
            candidate = _candidate(sample, x, y, axis, step, center)
            balance = (
                False
                if direction is None
                else active
                & (direction > 1)
                & candidate["valid"]
                & (candidate["truncation"] > candidate["rounding"])
            )
            update = (
                active
                & np.isfinite(candidate["value"])
                & ((candidate["score"] <= 1.01 * best_score) | ~np.isfinite(value))
            )
            eligible = active & candidate["eligible"] & ~np.asarray(balance)
            accepted = np.zeros(x.shape, dtype=bool)
            confirmed_error = candidate["error"]
            if np.any(eligible):
                # Freeze inactive points at already tested steps; retain callback
                # broadcast shape instead of silently flattening/subsetting it.
                probe = _candidate(sample, x, y, axis, step * 0.7, center)
                with np.errstate(all="ignore"):
                    agreement = np.abs(
                        probe["value"] - candidate["value"]
                    ) <= candidate["error"] + probe["error"] + 1e-6 * np.abs(
                        candidate["value"]
                    )
                    neighbor = (
                        True
                        if previous is None
                        else np.abs(candidate["value"] - previous["value"])
                        <= 4 * (candidate["error"] + previous["error"])
                        + 1e-6 * np.abs(candidate["value"])
                    )
                accepted = eligible & probe["eligible"] & agreement & neighbor
                if diagnostics:
                    confirmed_error = np.maximum(
                        candidate["error"],
                        np.maximum(
                            probe["error"], np.abs(probe["value"] - candidate["value"])
                        ),
                    )
                update |= accepted
                if diagnostics:
                    status = np.where(
                        accepted,
                        np.where(
                            candidate["stationary"],
                            "sampled_stationary",
                            "sample_consistent",
                        ),
                        status,
                    )
                    status = np.where(
                        accepted & candidate["flat"] & probe["flat"],
                        "flat_samples",
                        status,
                    )
            value = np.where(update, candidate["value"], value)
            best_score = np.where(update, candidate["score"], best_score)
            if diagnostics:
                error = np.where(
                    update,
                    np.where(accepted, confirmed_error, candidate["error"]),
                    error,
                )
                chosen_step = np.where(update, step, chosen_step)
                chosen_steps = tuple(
                    tuple(
                        np.where(update, new, old)
                        for new, old in zip(new_stencil, old_stencil)
                    )
                    for new_stencil, old_stencil in zip(
                        candidate["steps"], chosen_steps
                    )
                )
            done |= accepted
            stopped = active & candidate["collapsed"] & ~done
            if diagnostics:
                status = np.where(stopped, "stencil_collapsed", status)
                status = np.where(balance & ~done, "roundoff_limited", status)
            active &= ~done & ~stopped & ~np.asarray(balance)
            if direction is None:
                direction = np.where(
                    np.isfinite(candidate["value"])
                    & (candidate["rounding"] > candidate["truncation"]),
                    4.0,
                    0.25,
                )
            previous = candidate
            with np.errstate(all="ignore"):
                step = np.where(active, step * direction, step)
        gradients.append(value)
        if diagnostics:
            error = np.where(done, error, np.inf)
            status = np.where(~done & ~np.isfinite(value), "nonfinite", status)
            selection = np.where(
                chosen_step > anchor,
                "expanded",
                np.where(chosen_step < anchor, "refined", "local"),
            )
            errors.append(error)
            steps.append(chosen_steps)
            statuses.append(status)
            iterations.append(count)
            nominal_steps.append(chosen_step)
            selections.append(selection)
    return dict(
        gradient=tuple(gradients),
        error_estimate=tuple(errors),
        steps=tuple(steps),
        method="adaptive_richardson",
        status=tuple(statuses),
        candidates=tuple(iterations),
        nominal_step=tuple(nominal_steps),
        selection=tuple(selections),
        field_evaluations=evaluations,
        max_candidates=MAX_CANDIDATES,
    )
