import numpy as np
import pytest

from pdi_lab import ops


IDENTITY_3X3 = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.float64)


# ---------- convolve: guards ----------

def test_convolve_wrong_shape_raises():
    rgb = np.zeros((2, 2, 3), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.convolve(rgb, IDENTITY_3X3)


def test_convolve_empty_kernel_raises():
    gray = np.zeros((4, 4), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.convolve(gray, np.array([], dtype=np.float64).reshape(0, 0))


def test_convolve_non_square_kernel_raises():
    gray = np.zeros((4, 4), dtype=np.uint8)
    kernel = np.zeros((3, 5), dtype=np.float64)
    with pytest.raises(ops.OperationError):
        ops.convolve(gray, kernel)


def test_convolve_even_kernel_raises():
    gray = np.zeros((4, 4), dtype=np.uint8)
    kernel = np.zeros((2, 2), dtype=np.float64)
    with pytest.raises(ops.OperationError):
        ops.convolve(gray, kernel)


def test_convolve_invalid_border_raises():
    gray = np.zeros((4, 4), dtype=np.uint8)
    with pytest.raises(ops.OperationError):
        ops.convolve(gray, IDENTITY_3X3, border="invalido")


# ---------- convolve: identity kernel ----------

def test_identity_kernel_reproduces_image_replicate():
    gray = np.array([[10, 20, 30], [40, 50, 60], [70, 80, 90]], dtype=np.uint8)
    response = ops.convolve(gray, IDENTITY_3X3, border="replicate")
    out = ops.to_uint8(response)
    assert np.array_equal(out, gray)


def test_identity_kernel_reproduces_image_copy():
    gray = np.array([[10, 20, 30], [40, 50, 60], [70, 80, 90]], dtype=np.uint8)
    response = ops.convolve(gray, IDENTITY_3X3, border="copy")
    out = ops.to_uint8(response)
    assert np.array_equal(out, gray)


# ---------- convolve: constant image ----------

def test_constant_image_mean_filter_stays_constant():
    gray = np.full((6, 6), 100, dtype=np.uint8)
    out = ops.mean_filter(gray, border="replicate")
    assert np.all(out == 100)


# ---------- convolve: impulse ----------

def test_impulse_mean_filter_spreads_value():
    gray = np.zeros((5, 5), dtype=np.uint8)
    gray[2, 2] = 90
    out = ops.mean_filter(gray, border="replicate")
    # o pixel central da resposta deve ser 90/9 = 10
    assert out[2, 2] == round(90 / 9)
    # os vizinhos diretos tambem recebem contribuicao do impulso
    assert out[1, 2] > 0
    assert out[2, 1] > 0
    # pixels distantes do impulso nao sao afetados
    assert out[0, 0] == 0


# ---------- border strategies ----------

def test_border_copy_keeps_original_at_edges():
    gray = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.uint8)
    response = ops.convolve(gray, ops.MEAN_3X3, border="copy")
    out = ops.to_uint8(response)
    # cantos: vizinhanca nao cabe -> mantem valor original
    assert out[0, 0] == gray[0, 0]
    assert out[0, 2] == gray[0, 2]
    assert out[2, 0] == gray[2, 0]
    assert out[2, 2] == gray[2, 2]


def test_border_replicate_differs_from_copy_at_edges():
    gray = np.array([[0, 0, 0], [0, 255, 0], [0, 0, 0]], dtype=np.uint8)
    out_copy = ops.to_uint8(ops.convolve(gray, ops.MEAN_3X3, border="copy"))
    out_replicate = ops.to_uint8(ops.convolve(gray, ops.MEAN_3X3, border="replicate"))
    # no centro (vizinhanca cabe totalmente) as estrategias coincidem
    assert out_copy[1, 1] == out_replicate[1, 1]
    # no canto (vizinhanca nao cabe) as estrategias podem diferir
    assert out_copy[0, 0] == gray[0, 0]


# ---------- mean filters ----------

def test_mean_filter_reduces_variation():
    gray = np.array(
        [[0, 255, 0, 255], [255, 0, 255, 0], [0, 255, 0, 255], [255, 0, 255, 0]],
        dtype=np.uint8,
    )
    out = ops.mean_filter(gray, border="replicate")
    assert out.std() < gray.astype(np.float64).std()


def test_weighted_mean_filter_known_value():
    gray = np.full((3, 3), 100, dtype=np.uint8)
    out = ops.weighted_mean_filter(gray, border="replicate")
    assert out[1, 1] == 100


def test_mean_filter_5x5_shape():
    gray = np.zeros((7, 7), dtype=np.uint8)
    gray[3, 3] = 250
    response = ops.convolve(gray, ops.MEAN_5X5, border="replicate")
    out = ops.to_uint8(response)
    assert out.shape == gray.shape
    assert out[3, 3] == round(250 / 25)


# ---------- laplacian ----------

def test_laplacian_zero_on_constant_image():
    gray = np.full((5, 5), 128, dtype=np.uint8)
    result = ops.laplacian(gray, border="replicate")
    assert np.all(result["raw"] == 0)


def test_laplacian_can_be_negative_raw():
    gray = np.zeros((5, 5), dtype=np.uint8)
    gray[2, 2] = 255
    result = ops.laplacian(gray, border="replicate")
    assert (result["raw"] < 0).any() or (result["raw"] > 0).any()


def test_laplacian_step_edge_has_strong_response():
    gray = np.zeros((6, 6), dtype=np.uint8)
    gray[:, 3:] = 255
    result = ops.laplacian(gray, border="replicate")
    # a coluna da borda deve ter resposta com magnitude bem maior que 0
    assert np.abs(result["raw"][:, 3]).max() > 100


# ---------- sobel ----------

def test_sobel_vertical_step_responds_on_gx():
    gray = np.zeros((6, 6), dtype=np.uint8)
    gray[:, 3:] = 255  # degrau vertical -> bordas verticais
    result = ops.sobel(gray, border="replicate")
    gx_energy = np.abs(result["gx_raw"]).sum()
    gy_energy = np.abs(result["gy_raw"]).sum()
    assert gx_energy > gy_energy


def test_sobel_horizontal_step_responds_on_gy():
    gray = np.zeros((6, 6), dtype=np.uint8)
    gray[3:, :] = 255  # degrau horizontal -> bordas horizontais
    result = ops.sobel(gray, border="replicate")
    gx_energy = np.abs(result["gx_raw"]).sum()
    gy_energy = np.abs(result["gy_raw"]).sum()
    assert gy_energy > gx_energy


def test_sobel_magnitude_approx_vs_euclidean_differ():
    gray = np.array(
        [[10, 20, 30, 40], [15, 60, 35, 45], [20, 30, 80, 50], [25, 35, 45, 90]],
        dtype=np.uint8,
    )
    result = ops.sobel(gray, border="replicate")
    magnitude_approx = np.abs(result["gx_raw"]) + np.abs(result["gy_raw"])
    magnitude_euclidean = np.sqrt(result["gx_raw"] ** 2 + result["gy_raw"] ** 2)
    # para gradientes diagonais (Gx != 0 e Gy != 0), |Gx|+|Gy| > sqrt(Gx^2+Gy^2)
    assert np.any(magnitude_approx > magnitude_euclidean + 1e-6)


def test_sobel_constant_image_zero_response():
    gray = np.full((5, 5), 77, dtype=np.uint8)
    result = ops.sobel(gray, border="replicate")
    assert np.all(result["gx_raw"] == 0)
    assert np.all(result["gy_raw"] == 0)


# ---------- casos sinteticos adicionais exigidos pelo enunciado ----------

def test_1x1_image_convolution():
    gray = np.array([[42]], dtype=np.uint8)
    out = ops.to_uint8(ops.convolve(gray, IDENTITY_3X3, border="replicate"))
    assert out[0, 0] == 42


def test_2x2_image_convolution():
    gray = np.array([[10, 20], [30, 40]], dtype=np.uint8)
    out = ops.to_uint8(ops.convolve(gray, IDENTITY_3X3, border="replicate"))
    assert np.array_equal(out, gray)


def test_content_touching_border():
    gray = np.zeros((4, 4), dtype=np.uint8)
    gray[0, :] = 255  # linha superior tocando a borda
    out_replicate = ops.to_uint8(ops.convolve(gray, ops.MEAN_3X3, border="replicate"))
    out_copy = ops.to_uint8(ops.convolve(gray, ops.MEAN_3X3, border="copy"))
    # ambas devem produzir uma imagem valida do mesmo tamanho
    assert out_replicate.shape == gray.shape
    assert out_copy.shape == gray.shape
