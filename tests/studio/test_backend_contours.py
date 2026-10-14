"""Python/browser agreement on numerical edge cases, independent of scene UI."""

import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from geometry.static_blend import contours_from_grid

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "kind", ["tiny", "translated", "annulus", "touch", "edge", "extreme", "collapse"]
)
def test_browser_raw_grid_policy_matches_backend(kind):
    axis = np.linspace(-1, 1, 49)
    x, y = np.meshgrid(axis, axis)
    values = x * x + y * y - 0.55**2
    bounds = [-1, 1, -1, 1]
    resolution = 48
    if kind == "tiny":
        bounds = [-1e-9, 1e-9, -1e-9, 1e-9]
    if kind == "translated":
        bounds = [1e9 - 1, 1e9 + 1, 1e9 - 1, 1e9 + 1]
    if kind == "annulus":
        values = (x * x + y * y - 0.25**2) * (x * x + y * y - 0.7**2)
    if kind == "collapse":
        resolution = 24
        x, y = np.meshgrid(np.linspace(-1, 1, 25), np.linspace(-1, 1, 25))
        values = (x + 0.5) ** 2 + (y + 0.5) ** 2 - 0.2**2
        bounds = [1e16, 1e16 + 2, 1e16, 1e16 + 2]
    if kind == "touch":
        resolution = 4
        values = np.ones((5, 5))
        values[2, 2] = 0
        values[1, 1] = values[3, 3] = -1
    if kind == "edge":
        resolution = 1
        values = np.array([0, -1, -1, 0])
    if kind == "extreme":
        resolution = 4
        values = np.full((5, 5), 1e308)
        values[2, 2] = -1e308
    flat = values.ravel().tolist()
    code = "import {contoursFromGrid} from './studio/static/static-blend.js';let s='';for await(const c of process.stdin)s+=c;const p=JSON.parse(s);console.log(JSON.stringify(contoursFromGrid(p.values,p.bounds,[0],p.resolution)));"
    process = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        input=json.dumps(dict(values=flat, bounds=bounds, resolution=resolution)),
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    python = contours_from_grid(flat, bounds, [0], resolution)[0]
    browser = json.loads(process.stdout)[0]
    assert python["omitted"] == browser["omitted"]
    assert len(python["paths"]) == len(browser["paths"])
    for left, right in zip(python["paths"], browser["paths"]):
        np.testing.assert_allclose(left, right, rtol=1e-14, atol=1e-20)


def test_browser_rejects_nonfinite_grid_and_invalid_budget():
    code = "import {contoursFromGrid} from './studio/static/static-blend.js';let rejected=0;for(const bad of [NaN,Infinity,-Infinity]){try{contoursFromGrid([1,1,1,bad],[0,1,0,1],[0],1)}catch{rejected++}}for(const res of [0,193,true]){try{contoursFromGrid([1,1,1,1],[0,1,0,1],[0],res)}catch{rejected++}}console.log(rejected);"
    process = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    assert int(process.stdout) == 6
