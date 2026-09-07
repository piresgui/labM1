import numpy as np
import pytest

from pdi_lab import ops


def make_image(pixels):
    """pixels: lista 2D de tuplas (r,g,b) -> array (H, W, 3) uint8."""
    return np.array(pixels, dtype=np.uint8)


# ---------- inspect ----------

def test_inspect_1x1():
    img = make_image([[[10, 20, 30]]])
    stats = ops.inspect(img)
    assert stats["width"] == 1
    assert stats["height"] == 1
    assert stats["channels"] == 3
    assert stats["pixels"] == 1
    assert stats["min"] == 10
    assert stats["max"] == 30
    assert stats["mean"] == pytest.approx(20.0)
    assert stats["channel_mean"] == [10.0, 20.0, 30.0]


def test_inspect_constant_image():
    img = np.full((4, 4, 3), 100, dtype=np.uint8)
    stats = ops.inspect(img)
    assert stats["min"] == 100
    assert stats["max"] == 100
    assert stats["mean"] == pytest.approx(100.0)


def test_inspect_wrong_channels_raises():
    img = np.zeros((2, 2), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.inspect(img)


# ---------- copy ----------

def test_copy_is_numerically_identical():
    rng_values = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
    img = make_image(rng_values)
    out = ops.copy_manual(img)
    assert np.array_equal(out, img)
    assert out is not img


def test_copy_2x2():
    img = make_image([[[0, 0, 0], [255, 255, 255]], [[10, 20, 30], [40, 50, 60]]])
    out = ops.copy_manual(img)
    assert np.array_equal(out, img)


# ---------- channel isolation ----------

def test_channel_r_isolation():
    img = make_image([[[10, 20, 30]]])
    out = ops.channel_isolate(img, "r")
    assert out[0, 0, 0] == 10
    assert out[0, 0, 1] == 0
    assert out[0, 0, 2] == 0


def test_channel_g_isolation():
    img = make_image([[[10, 20, 30]]])
    out = ops.channel_isolate(img, "g")
    assert list(out[0, 0]) == [0, 20, 0]


def test_channel_b_isolation():
    img = make_image([[[10, 20, 30]]])
    out = ops.channel_isolate(img, "b")
    assert list(out[0, 0]) == [0, 0, 30]


def test_channel_invalid_raises():
    img = make_image([[[10, 20, 30]]])
    with pytest.raises(ops.OperationError):
        ops.channel_isolate(img, "x")


# ---------- grayscale ----------

def test_grayscale_average_known_value():
    img = make_image([[[9, 6, 3]]])  # (9+6+3)/3 = 6
    out = ops.grayscale_average(img)
    assert out[0, 0] == 6


def test_grayscale_weighted_known_value():
    img = make_image([[[100, 100, 100]]])
    out = ops.grayscale_weighted(img)
    assert out[0, 0] == 100  # combinacao convexa de pesos que somam 1


def test_grayscale_average_vs_weighted_differ():
    img = make_image([[[255, 0, 0]]])
    avg = ops.grayscale_average(img)
    weighted = ops.grayscale_weighted(img)
    assert avg[0, 0] != weighted[0, 0]


def test_grayscale_saturation_at_limits():
    img = make_image([[[255, 255, 255], [0, 0, 0]]])
    avg = ops.grayscale_average(img)
    assert avg[0, 0] == 255
    assert avg[0, 1] == 0


# ---------- quantize ----------

def test_quantize_2_levels_produces_two_distinct_values():
    gray = np.array([[0, 64, 128, 255]], dtype=np.uint8)
    out = ops.quantize(gray, 2)
    distinct = set(out.flatten().tolist())
    assert len(distinct) <= 2


def test_quantize_16_levels_within_range():
    gray = np.arange(256, dtype=np.uint8).reshape(16, 16)
    out = ops.quantize(gray, 16)
    assert out.min() >= 0
    assert out.max() <= 255
    distinct = set(out.flatten().tolist())
    assert len(distinct) <= 16


def test_quantize_invalid_levels_raises():
    gray = np.zeros((2, 2), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.quantize(gray, 1)
    with pytest.raises(ops.OperationError):
        ops.quantize(gray, 0)
    with pytest.raises(ops.OperationError):
        ops.quantize(gray, 257)


def test_quantize_boundary_values():
    gray = np.array([[0, 255]], dtype=np.uint8)
    out = ops.quantize(gray, 4)
    assert out[0, 0] < out[0, 1]
