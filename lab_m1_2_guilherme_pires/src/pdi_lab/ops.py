"""Operacoes do Laboratorio M1.2, implementadas manualmente pixel a pixel.

Cada pixel de saida depende apenas do pixel correspondente da imagem de
entrada em niveis de cinza (transformacoes pontuais).

Nenhuma funcao pronta de biblioteca realiza diretamente as operacoes
avaliadas (brilho, contraste, negativo, limiarizacao, histograma); numpy e
usado apenas para alocar as matrizes de saida e Pillow apenas para abrir e
salvar arquivos.
"""

from __future__ import annotations

import numpy as np


class OperationError(ValueError):
    """Erro de uso/parametro em uma operacao do laboratorio."""


def _saturate_round(value: float) -> int:
    rounded = int(round(value))
    if rounded < 0:
        return 0
    if rounded > 255:
        return 255
    return rounded


def grayscale_weighted(image_rgb: np.ndarray) -> np.ndarray:
    """Conversao manual para niveis de cinza por media ponderada
    (g = 0.299 R + 0.587 G + 0.114 B)."""

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


def _check_gray(image_gray: np.ndarray, op_name: str) -> None:
    if image_gray.ndim != 2:
        raise OperationError(f"{op_name} espera uma imagem em niveis de cinza (H, W)")


def brightness(image_gray: np.ndarray, b: float) -> np.ndarray:
    """g(x,y) = f(x,y) + b, com saturacao em [0, 255]."""

    _check_gray(image_gray, "brightness")
    if not isinstance(b, (int, float)):
        raise OperationError("valor de brilho (--value) invalido")

    height, width = image_gray.shape
    out = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            value = int(image_gray[y, x]) + b
            out[y, x] = _saturate_round(value)

    return out


def contrast(image_gray: np.ndarray, alpha: float) -> np.ndarray:
    """g(x,y) = alpha*(f(x,y) - 128) + 128, com saturacao em [0, 255]."""

    _check_gray(image_gray, "contrast")
    if not isinstance(alpha, (int, float)) or alpha < 0:
        raise OperationError(
            f"valor de alpha invalido: {alpha} (deve ser um numero >= 0)"
        )

    height, width = image_gray.shape
    out = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            value = alpha * (int(image_gray[y, x]) - 128) + 128
            out[y, x] = _saturate_round(value)

    return out


def negative(image_gray: np.ndarray) -> np.ndarray:
    """g(x,y) = 255 - f(x,y)."""

    _check_gray(image_gray, "negative")

    height, width = image_gray.shape
    out = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            out[y, x] = 255 - int(image_gray[y, x])

    return out


def threshold(image_gray: np.ndarray, t: int) -> np.ndarray:
    """Limiarizacao binaria: g(x,y) = 0 se f(x,y) < T, senao 255."""

    _check_gray(image_gray, "threshold")
    if not isinstance(t, (int, float)) or t < 0 or t > 255:
        raise OperationError(
            f"limiar invalido: {t} (deve estar no intervalo [0, 255])"
        )

    height, width = image_gray.shape
    out = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            out[y, x] = 255 if int(image_gray[y, x]) >= t else 0

    return out


def histogram(image_gray: np.ndarray) -> list[int]:
    """Conta manualmente quantos pixels possuem cada intensidade (0..255)."""

    _check_gray(image_gray, "histogram")

    counts = [0] * 256
    height, width = image_gray.shape

    for y in range(height):
        for x in range(width):
            value = int(image_gray[y, x])
            counts[value] += 1

    return counts
