import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
KERNELS = os.path.join(ROOT, "kernels")


def run_cli(args, cwd):
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC
    cmd = [sys.executable, "-m", "pdi_lab"] + args
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def make_png(path, pixels):
    arr = np.array(pixels, dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def test_cli_missing_input_file(tmp_path):
    result = run_cli(
        ["--input", "nope.png", "--output", str(tmp_path), "--operation", "mean_filter"],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0
    assert "erro" in result.stderr.lower()


def test_cli_convolution_missing_kernel_fails(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 10, 10], [20, 20, 20]], [[30, 30, 30], [40, 40, 40]]])
    result = run_cli(
        ["--input", str(img_path), "--output", str(tmp_path / "out.png"), "--operation", "convolution"],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0


def test_cli_convolution_missing_kernel_file_fails(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 10, 10], [20, 20, 20]], [[30, 30, 30], [40, 40, 40]]])
    result = run_cli(
        [
            "--input", str(img_path),
            "--output", str(tmp_path / "out.png"),
            "--operation", "convolution",
            "--kernel", str(tmp_path / "nao_existe.txt"),
        ],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0


def test_cli_convolution_identity_success(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 10, 10], [20, 20, 20]], [[30, 30, 30], [40, 40, 40]]])
    out_path = tmp_path / "out.png"
    result = run_cli(
        [
            "--input", str(img_path),
            "--output", str(out_path),
            "--operation", "convolution",
            "--kernel", os.path.join(KERNELS, "identity_3x3.txt"),
            "--border", "replicate",
        ],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert out_path.exists()
    out_arr = np.array(Image.open(out_path))
    assert np.array_equal(out_arr, np.array([[10, 20], [30, 40]], dtype=np.uint8))


def test_cli_invalid_border_fails(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[10, 10, 10]]])
    result = run_cli(
        [
            "--input", str(img_path),
            "--output", str(tmp_path / "out.png"),
            "--operation", "convolution",
            "--kernel", os.path.join(KERNELS, "identity_3x3.txt"),
            "--border", "invalida",
        ],
        cwd=str(tmp_path),
    )
    assert result.returncode != 0


def test_cli_mean_filter_default_kernel(tmp_path):
    img_path = tmp_path / "in.png"
    make_png(str(img_path), [[[100, 100, 100]] * 3] * 3)
    out_path = tmp_path / "out.png"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "mean_filter"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    out_arr = np.array(Image.open(out_path))
    assert out_arr[1, 1] == 100


def test_cli_laplacian_produces_two_outputs(tmp_path):
    img_path = tmp_path / "in.png"
    pixels = [[[0, 0, 0]] * 6 for _ in range(6)]
    for y in range(6):
        for x in range(3, 6):
            pixels[y][x] = [255, 255, 255]
    make_png(str(img_path), pixels)
    out_path = tmp_path / "lap.png"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "laplacian"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert out_path.exists()
    assert (tmp_path / "lap_enhanced.png").exists()


def test_cli_sobel_produces_four_outputs(tmp_path):
    img_path = tmp_path / "in.png"
    pixels = [[[0, 0, 0]] * 6 for _ in range(6)]
    for y in range(6):
        for x in range(3, 6):
            pixels[y][x] = [255, 255, 255]
    make_png(str(img_path), pixels)
    out_path = tmp_path / "sob.png"
    result = run_cli(
        ["--input", str(img_path), "--output", str(out_path), "--operation", "sobel"],
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert (tmp_path / "sob_gx.png").exists()
    assert (tmp_path / "sob_gy.png").exists()
    assert (tmp_path / "sob_magnitude_approx.png").exists()
    assert (tmp_path / "sob_magnitude_euclidean.png").exists()
