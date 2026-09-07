import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")


def run_cli(args, cwd):
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC
    cmd = [sys.executable, "-m", "pdi_lab"] + args
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def make_png(path, pixels):
    arr = np.array(pixels, dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def test_cli_missing_file_returns_nonzero(tmp_path):
    result = run_cli(
        ["--input", "does_not_exist.png", "--output", str(tmp_path), "--operation", "inspect"],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0
    assert "erro" in result.stderr.lower()


def test_cli_inspect_success(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 20, 30], [40, 50, 60]]])
    result = run_cli(
        ["--input", str(img_path), "--output", str(tmp_path), "--operation", "inspect"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert "width=2" in result.stdout
    assert "height=1" in result.stdout


def test_cli_copy_generates_identical_output(tmp_path):
    img_path = tmp_path / "in.png"
    pixels = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
    make_png(str(img_path), pixels)
    out_path = tmp_path / "copy.png"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "copy"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    out_arr = np.array(Image.open(out_path).convert("RGB"))
    assert np.array_equal(out_arr, np.array(pixels, dtype=np.uint8))


def test_cli_quantize_missing_levels_fails(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 20, 30]]])
    out_path = tmp_path / "q.png"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "quantize"],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0


def test_cli_quantize_success(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 20, 30], [200, 210, 220]]])
    out_path = tmp_path / "q.png"
    result = run_cli(
        [
            "--input", str(img_path),
            "--output", str(out_path),
            "--operation", "quantize",
            "--levels", "4",
        ],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert out_path.exists()
