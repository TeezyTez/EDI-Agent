from pathlib import Path
import subprocess
import sys


def run_pytest(test_dir: str | Path) -> tuple[bool, str]:
    """Run pytest in a subprocess and return pass/fail with captured output."""
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_dir), "-q"],
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    return completed.returncode == 0, output
