import numpy as np
import pytest

from pdi_lab import ops


# ---------- brightness ----------

def test_brightness_positive():
    gray = np.array([[100, 200]], dtype=np.uint8)
    out = ops.brightness(gray, 30)
    assert out[0, 0] == 130
    assert out[0, 1] == 230


def test_brightness_negative():
    gray = np.array([[100, 200]], dtype=np.uint8)
    out = ops.brightness(gray, -50)
    assert out[0, 0] == 50
    assert out[0, 1] == 150


def test_brightness_saturates_high():
    gray = np.array([[250]], dtype=np.uint8)
    out = ops.brightness(gray, 30)
    assert out[0, 0] == 255


def test_brightness_saturates_low():
    gray = np.array([[10]], dtype=np.uint8)
    out = ops.brightness(gray, -50)
    assert out[0, 0] == 0


def test_brightness_wrong_shape_raises():
    rgb = np.zeros((2, 2, 3), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.brightness(rgb, 10)


# ---------- contrast ----------

def test_contrast_identity_alpha_1():
    gray = np.array([[0, 128, 255]], dtype=np.uint8)
    out = ops.contrast(gray, 1.0)
    assert list(out[0]) == [0, 128, 255]


def test_contrast_reduced_alpha_0_5():
    gray = np.array([[0, 255]], dtype=np.uint8)
    out = ops.contrast(gray, 0.5)
    # (0-128)*0.5+128 = 64 ; (255-128)*0.5+128 = 191.5 -> 192 (round-half-to-even is fine too)
    assert out[0, 0] == 64
    assert out[0, 1] in (191, 192)


def test_contrast_amplified_alpha_1_5_saturates():
    gray = np.array([[0, 255]], dtype=np.uint8)
    out = ops.contrast(gray, 1.5)
    assert out[0, 0] == 0  # (0-128)*1.5+128 = -64 -> satura em 0
    assert out[0, 1] == 255  # (255-128)*1.5+128 = 318.5 -> satura em 255


def test_contrast_negative_alpha_raises():
    gray = np.array([[10]], dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.contrast(gray, -1.0)


# ---------- negative ----------

def test_negative_known_values():
    gray = np.array([[0, 128, 255]], dtype=np.uint8)
    out = ops.negative(gray)
    assert list(out[0]) == [255, 127, 0]


def test_negative_wrong_shape_raises():
    rgb = np.zeros((2, 2, 3), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.negative(rgb)


# ---------- threshold ----------

def test_threshold_two_values():
    gray = np.array([[50, 100, 150, 200]], dtype=np.uint8)
    out_low = ops.threshold(gray, 100)
    assert list(out_low[0]) == [0, 255, 255, 255]
    out_high = ops.threshold(gray, 180)
    assert list(out_high[0]) == [0, 0, 0, 255]


def test_threshold_invalid_raises():
    gray = np.array([[10]], dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.threshold(gray, -1)
    with pytest.raises(ops.OperationError):
        ops.threshold(gray, 256)


# ---------- histogram ----------

def test_histogram_length_and_sum():
    gray = np.array([[0, 0, 255], [10, 10, 10]], dtype=np.uint8)
    counts = ops.histogram(gray)
    assert len(counts) == 256
    assert sum(counts) == gray.size
    assert counts[0] == 2
    assert counts[10] == 3
    assert counts[255] == 1


def test_histogram_constant_image():
    gray = np.full((3, 3), 42, dtype=np.uint8)
    counts = ops.histogram(gray)
    assert counts[42] == 9
    assert sum(counts) == 9


def test_histogram_impulse():
    gray = np.zeros((4, 4), dtype=np.uint8)
    gray[2, 2] = 255
    counts = ops.histogram(gray)
    assert counts[0] == 15
    assert counts[255] == 1


def test_histogram_wrong_shape_raises():
    rgb = np.zeros((2, 2, 3), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.histogram(rgb)


# ---------- grayscale_weighted (reuso do M1.1) ----------

def test_grayscale_weighted_basic():
    rgb = np.array([[[100, 100, 100]]], dtype=np.uint8)
    out = ops.grayscale_weighted(rgb)
    assert out[0, 0] == 100
