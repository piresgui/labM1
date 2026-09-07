import numpy as np
import pytest

from pdi_lab import io_utils


def write_kernel(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def test_load_kernel_valid(tmp_path):
    path = tmp_path / "k.txt"
    write_kernel(path, "3 3\n0 0 0\n0 1 0\n0 0 0\n")
    kernel = io_utils.load_kernel(str(path))
    assert kernel.shape == (3, 3)
    assert kernel[1, 1] == 1


def test_load_kernel_missing_file_raises(tmp_path):
    with pytest.raises(io_utils.KernelError):
        io_utils.load_kernel(str(tmp_path / "nope.txt"))


def test_load_kernel_empty_raises(tmp_path):
    path = tmp_path / "k.txt"
    write_kernel(path, "")
    with pytest.raises(io_utils.KernelError):
        io_utils.load_kernel(str(path))


def test_load_kernel_wrong_value_count_raises(tmp_path):
    path = tmp_path / "k.txt"
    write_kernel(path, "3 3\n0 0 0\n0 1 0\n0 0\n")  # faltando um valor
    with pytest.raises(io_utils.KernelError):
        io_utils.load_kernel(str(path))


def test_load_kernel_not_square_raises(tmp_path):
    path = tmp_path / "k.txt"
    write_kernel(path, "2 3\n0 0 0\n0 0 0\n")
    with pytest.raises(io_utils.KernelError):
        io_utils.load_kernel(str(path))


def test_load_kernel_even_dimension_raises(tmp_path):
    path = tmp_path / "k.txt"
    write_kernel(path, "2 2\n1 1\n1 1\n")
    with pytest.raises(io_utils.KernelError):
        io_utils.load_kernel(str(path))


def test_load_kernel_non_numeric_raises(tmp_path):
    path = tmp_path / "k.txt"
    write_kernel(path, "3 3\n0 0 0\n0 x 0\n0 0 0\n")
    with pytest.raises(io_utils.KernelError):
        io_utils.load_kernel(str(path))


def test_validate_kernel_valid_kernel_passes():
    kernel = np.zeros((3, 3))
    io_utils.validate_kernel(kernel)  # nao deve lancar


def test_load_image_missing_file_raises():
    with pytest.raises(io_utils.ImageLoadError):
        io_utils.load_image_gray("does_not_exist.png")
