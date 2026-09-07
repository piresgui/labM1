"""Operacoes do Laboratorio M1.3: convolucao generica e filtros espaciais,
implementados manualmente (percurso explicito da vizinhanca, sem usar
convolucao pronta de nenhuma biblioteca).

Convencoes:
- Imagens de entrada/saida em niveis de cinza sao arrays uint8 (H, W).
- Durante o calculo, os acumuladores usam float64 para evitar overflow e
  permitir valores negativos (Laplaciano, Sobel) antes da saturacao final.
- Saturacao para uint8 [0, 255] e feita somente no momento de produzir a
  imagem final.
"""

from __future__ import annotations

import numpy as np

BORDER_STRATEGIES = ("copy", "replicate")


class OperationError(ValueError):
    """Erro de uso/parametro em uma operacao do laboratorio."""


def grayscale_weighted(image_rgb: np.ndarray) -> np.ndarray:
    """Conversao manual para niveis de cinza por media ponderada
    (g = 0.299 R + 0.587 G + 0.114 B), reaproveitada dos laboratorios
    anteriores para preparar a entrada da convolucao."""

    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise OperationError("grayscale_weighted espera uma imagem RGB (H, W, 3)")

    height, width, _ = image_rgb.shape
    out = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            r = int(image_rgb[y, x, 0])
            g = int(image_rgb[y, x, 1])
            b = int(image_rgb[y, x, 2])
            value = 0.299 * r + 0.587 * g + 0.114 * b
            out[y, x] = _saturate_round(value)

    return out


def _saturate_round(value: float) -> int:
    rounded = int(round(value))
    if rounded < 0:
        return 0
    if rounded > 255:
        return 255
    return rounded


def _check_gray(image_gray: np.ndarray, op_name: str) -> None:
    if image_gray.ndim != 2:
        raise OperationError(f"{op_name} espera uma imagem em niveis de cinza (H, W)")


def _resolve_coordinate(coord: int, limit: int, border: str) -> int | None:
    """Resolve uma coordenada (linha ou coluna) de vizinhanca fora da
    imagem, de acordo com a estrategia de borda.

    Retorna None quando a estrategia for "copy" e a coordenada estiver fora
    dos limites (sinaliza ao chamador que o pixel de saida deve manter o
    valor original, sem processar a vizinhanca completa).
    """

    if 0 <= coord < limit:
        return coord

    if border == "replicate":
        if coord < 0:
            return 0
        return limit - 1

    if border == "copy":
        return None

    raise OperationError(f"estrategia de borda invalida: {border}")


def convolve(image_gray: np.ndarray, kernel: np.ndarray, border: str = "replicate") -> np.ndarray:
    """Convolucao espacial generica, manual, com tratamento de borda.

    - image_gray: imagem em niveis de cinza (H, W), uint8.
    - kernel: matriz quadrada de dimensao impar (float64).
    - border: "copy" (pixels onde a vizinhanca nao cabe mantem o valor
      original) ou "replicate" (coordenadas fora da imagem sao substituidas
      pela coordenada valida mais proxima).

    Retorna a resposta bruta em float64 (pode conter valores negativos e
    maiores que 255) — a saturacao para visualizacao/gravacao deve ser
    aplicada pelo chamador com `to_uint8`.
    """

    _check_gray(image_gray, "convolve")

    if kernel.ndim != 2:
        raise OperationError("kernel deve ser uma matriz 2D")

    krows, kcols = kernel.shape
    if kernel.size == 0:
        raise OperationError("kernel vazio")
    if krows != kcols:
        raise OperationError(f"kernel nao e quadrado: {krows}x{kcols}")
    if krows % 2 == 0:
        raise OperationError(f"kernel de dimensao par nao permitido: {krows}x{kcols}")

    if border not in BORDER_STRATEGIES:
        raise OperationError(f"estrategia de borda invalida: {border}")

    height, width = image_gray.shape
    radius = krows // 2

    # acumulador em float64 para evitar overflow e permitir negativos
    response = np.zeros((height, width), dtype=np.float64)
    image_f64 = image_gray.astype(np.float64)

    for y in range(height):
        for x in range(width):
            fits = (
                y - radius >= 0
                and y + radius < height
                and x - radius >= 0
                and x + radius < width
            )

            if not fits and border == "copy":
                response[y, x] = image_f64[y, x]
                continue

            accumulator = 0.0
            for ky in range(krows):
                for kx in range(kcols):
                    ny = y + (ky - radius)
                    nx = x + (kx - radius)

                    ry = _resolve_coordinate(ny, height, border)
                    rx = _resolve_coordinate(nx, width, border)
                    # quando border == "replicate", ry/rx nunca sao None
                    accumulator += image_f64[ry, rx] * kernel[ky, kx]

            response[y, x] = accumulator

    return response


def to_uint8(response: np.ndarray) -> np.ndarray:
    """Satura uma resposta em float64 para uint8 [0, 255], arredondando."""

    height, width = response.shape
    out = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            out[y, x] = _saturate_round(response[y, x])
    return out


def to_uint8_normalized(response: np.ndarray) -> np.ndarray:
    """Normaliza uma resposta (que pode ter valores negativos ou > 255)
    linearmente para o intervalo [0, 255], para fins de visualizacao.

    Usado para a resposta bruta do Laplaciano, que pode conter negativos.
    Se a resposta for constante, produz uma imagem constante em 128.
    """

    height, width = response.shape
    resp_min = response.min()
    resp_max = response.max()

    out = np.zeros((height, width), dtype=np.uint8)

    if resp_max == resp_min:
        out[:, :] = 128
        return out

    scale = 255.0 / (resp_max - resp_min)
    for y in range(height):
        for x in range(width):
            value = (response[y, x] - resp_min) * scale
            out[y, x] = _saturate_round(value)
    return out


# ---------------------------------------------------------------------
# Kernels padronizados
# ---------------------------------------------------------------------

MEAN_3X3 = np.full((3, 3), 1.0 / 9.0, dtype=np.float64)

WEIGHTED_MEAN_3X3 = np.array(
    [[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float64
) / 16.0

MEAN_5X5 = np.full((5, 5), 1.0 / 25.0, dtype=np.float64)

# Laplaciano com centro negativo (resposta positiva em bordas de intensidade
# crescente na direcao dos vizinhos); documentado conforme exigido.
LAPLACIAN_KERNEL = np.array(
    [[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float64
)

SOBEL_GX = np.array(
    [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64
)

SOBEL_GY = np.array(
    [[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64
)


def mean_filter(image_gray: np.ndarray, border: str = "replicate") -> np.ndarray:
    """Filtro de media 3x3."""
    response = convolve(image_gray, MEAN_3X3, border)
    return to_uint8(response)


def weighted_mean_filter(image_gray: np.ndarray, border: str = "replicate") -> np.ndarray:
    """Filtro de media ponderada 3x3."""
    response = convolve(image_gray, WEIGHTED_MEAN_3X3, border)
    return to_uint8(response)


def mean_filter_5x5(image_gray: np.ndarray, border: str = "replicate") -> np.ndarray:
    """Filtro de media 5x5."""
    response = convolve(image_gray, MEAN_5X5, border)
    return to_uint8(response)


def laplacian(image_gray: np.ndarray, border: str = "replicate") -> dict:
    """Aplica o kernel Laplaciano e retorna a resposta bruta (float64,
    pode conter negativos), a versao normalizada para visualizacao e a
    imagem realcada (original + resposta bruta, saturada)."""

    raw = convolve(image_gray, LAPLACIAN_KERNEL, border)
    visualization = to_uint8_normalized(raw)

    enhanced_f64 = image_gray.astype(np.float64) + raw
    enhanced = to_uint8(enhanced_f64)

    return {"raw": raw, "visualization": visualization, "enhanced": enhanced}


def sobel(image_gray: np.ndarray, border: str = "replicate") -> dict:
    """Calcula Gx, Gy, magnitude aproximada (|Gx|+|Gy|) e magnitude
    euclidiana (sqrt(Gx^2+Gy^2)). Mantem tipos numericos adequados
    (float64) durante o calculo e satura somente na imagem final."""

    gx = convolve(image_gray, SOBEL_GX, border)
    gy = convolve(image_gray, SOBEL_GY, border)

    magnitude_approx = np.abs(gx) + np.abs(gy)
    magnitude_euclidean = np.sqrt(gx.astype(np.float64) ** 2 + gy.astype(np.float64) ** 2)

    return {
        "gx_raw": gx,
        "gy_raw": gy,
        "gx": to_uint8_normalized(gx),
        "gy": to_uint8_normalized(gy),
        "magnitude_approx": to_uint8(magnitude_approx),
        "magnitude_euclidean": to_uint8(magnitude_euclidean),
    }
