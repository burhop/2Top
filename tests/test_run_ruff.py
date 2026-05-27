import subprocess

import os

import sys

def test_run_ruff():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "."],
        capture_output=True,
        text=True,
        cwd=root
    )
    # Write output to a file so we can easily view it
    output_path = os.path.join(root, "scratch_ruff_output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
    
    # Assert return code is 0 to let the test pass if Ruff succeeds
    assert result.returncode == 0, f"Ruff finished with exit code {result.returncode}. Output:\n{result.stdout}\n{result.stderr}"
