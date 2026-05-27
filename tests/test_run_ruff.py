import subprocess

def test_run_ruff():
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "."],
        capture_output=True,
        text=True,
        cwd="d:\\repos\\2Top"
    )
    # Write output to a file so we can easily view it
    with open("d:\\repos\\2Top\\scratch_ruff_output.txt", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
    
    # Assert False to make pytest print it if we want, or just let it pass
    assert False, f"Ruff finished with exit code {result.returncode}. Output written to scratch_ruff_output.txt"
