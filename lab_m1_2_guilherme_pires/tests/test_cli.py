import csv
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
        ["--input", "nope.png", "--output", str(tmp_path), "--operation", "negative"],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0
    assert "erro" in result.stderr.lower()


def test_cli_brightness_missing_value_fails(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[100, 100, 100]]])
    result = run_cli(
        ["--input", str(img_path), "--output", str(tmp_path / "out.png"), "--operation", "brightness"],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0


def test_cli_brightness_success(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[100, 100, 100]]])
    out_path = tmp_path / "out.png"
    result = run_cli(
        [
            "--input", str(img_path),
            "--output", str(out_path),
            "--operation", "brightness",
            "--value", "30",
        ],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert out_path.exists()
    out_arr = np.array(Image.open(out_path))
    assert out_arr[0, 0] == 130


def test_cli_threshold_two_values(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[50, 50, 50], [150, 150, 150]]])
    out1 = tmp_path / "t100.png"
    out2 = tmp_path / "t180.png"
    r1 = run_cli(
        ["--input", str(img_path), "--output", str(out1), "--operation", "threshold", "--threshold", "100"],
        cwd=str(tmp_path),
    )
    r2 = run_cli(
        ["--input", str(img_path), "--output", str(out2), "--operation", "threshold", "--threshold", "160"],
        cwd=str(tmp_path),
    )
    assert r1.returncode == 0 and r2.returncode == 0
    arr1 = np.array(Image.open(out1))
    arr2 = np.array(Image.open(out2))
    assert not np.array_equal(arr1, arr2)


def test_cli_histogram_csv_format(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[0, 0, 0], [255, 255, 255]]])
    out_path = tmp_path / "hist.csv"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "histogram"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    with open(out_path, newline="", encoding="utf-8") as fh:
        reader = list(csv.reader(fh))
    assert reader[0] == ["intensity", "count"]
    assert len(reader) == 257  # header + 256 linhas
    total = sum(int(row[1]) for row in reader[1:])
    assert total == 2


def test_cli_negative_success(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[0, 0, 0], [255, 255, 255]]])
    out_path = tmp_path / "neg.png"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "negative"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    arr = np.array(Image.open(out_path))
    assert arr[0, 0] == 255
    assert arr[0, 1] == 0
