"""Operacoes do Laboratorio M1.1, implementadas manualmente pixel a pixel.

Convencao de canais: as imagens de entrada sao sempre convertidas para RGB
antes de chegar a estas funcoes (ver io_utils.load_image_rgb), portanto o
indice 0 e sempre o canal R (vermelho), 1 e G (verde) e 2 e B (azul).

Nenhuma funcao pronta de biblioteca (cv2.cvtColor, ImageOps, np.mean sobre a
imagem inteira etc.) e usada para realizar as operacoes avaliadas: o percurso
e feito com loops explicitos sobre linhas e colunas.
"""

from __future__ import annotations

import numpy as np


class OperationError(ValueError):
    """Erro de uso/parametro em uma operacao do laboratorio."""


def inspect(image_rgb: np.ndarray) -> dict:
    """Calcula estatisticas manuais da imagem (dimensoes, min/max/media
    gerais e por canal)."""

    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise OperationError("inspect espera uma imagem RGB (H, W, 3)")

    height, width, channels = image_rgb.shape
    pixels = width * height

    total_sum = 0
    total_count = 0
    overall_min = 255
    overall_max = 0

    channel_sum = [0, 0, 0]
    channel_count = [0, 0, 0]
    channel_min = [255, 255, 255]
    channel_max = [0, 0, 0]

    for y in range(height):
        for x in range(width):
            for c in range(channels):
                value = int(image_rgb[y, x, c])
                total_sum += value
                total_count += 1
                if value < overall_min:
                    overall_min = value
                if value > overall_max:
                    overall_max = value

                channel_sum[c] += value
                channel_count[c] += 1
                if value < channel_min[c]:
                    channel_min[c] = value
                if value > channel_max[c]:
                    channel_max[c] = value

    overall_mean = total_sum / total_count if total_count else 0.0
    channel_mean = [
        (channel_sum[c] / channel_count[c] if channel_count[c] else 0.0)
        for c in range(channels)
    ]

    return {
        "width": width,
        "height": height,
        "channels": channels,
        "pixels": pixels,
        "dtype": str(image_rgb.dtype),
        "min": overall_min,
        "max": overall_max,
        "mean": overall_mean,
        "channel_min": channel_min,
        "channel_max": channel_max,
        "channel_mean": channel_mean,
    }


def copy_manual(image_rgb: np.ndarray) -> np.ndarray:
    """Copia manual: cria uma nova imagem e copia cada pixel individualmente."""

    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise OperationError("copy espera uma imagem RGB (H, W, 3)")

    height, width, channels = image_rgb.shape
    out = np.zeros((height, width, channels), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            for c in range(channels):
                out[y, x, c] = image_rgb[y, x, c]

    return out


_CHANNEL_INDEX = {"r": 0, "g": 1, "b": 2}


def channel_isolate(image_rgb: np.ndarray, channel: str) -> np.ndarray:
    """Gera uma imagem RGB preservando somente o canal solicitado e zerando
    os demais."""

    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise OperationError("channel_* espera uma imagem RGB (H, W, 3)")

    channel = channel.lower()
    if channel not in _CHANNEL_INDEX:
        raise OperationError(f"canal invalido: {channel} (use r, g ou b)")

    keep = _CHANNEL_INDEX[channel]
    height, width, channels = image_rgb.shape
    out = np.zeros((height, width, channels), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            out[y, x, keep] = image_rgb[y, x, keep]

    return out


def grayscale_average(image_rgb: np.ndarray) -> np.ndarray:
    """Conversao manual para niveis de cinza por media simples: g=(R+G+B)/3."""

    if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
        raise OperationError("grayscale_average espera uma imagem RGB (H, W, 3)")

    height, width, _ = image_rgb.shape
    out = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            r = int(image_rgb[y, x, 0])
            g = int(image_rgb[y, x, 1])
            b = int(image_rgb[y, x, 2])
            value = (r + g + b) / 3.0
            out[y, x] = _saturate_round(value)

    return out


def grayscale_weighted(image_rgb: np.ndarray) -> np.ndarray:
    """Conversao manual para niveis de cinza por media ponderada
    (g = 0.299 R + 0.587 G + 0.114 B), conforme a formula padrao de luminancia."""

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


def quantize(image_gray: np.ndarray, levels: int) -> np.ndarray:
    """Quantiza manualmente uma imagem em niveis de cinza (0-255) para
    `levels` niveis distintos, mantendo os valores no intervalo [0, 255].

    A largura de cada faixa e 256/levels; o valor representativo de cada
    faixa e o seu ponto medio, arredondado e saturado.
    """

    if image_gray.ndim != 2:
        raise OperationError("quantize espera uma imagem em niveis de cinza (H, W)")

    if not isinstance(levels, int) or levels < 2 or levels > 256:
        raise OperationError(
            f"quantidade de niveis invalida: {levels} (deve ser um inteiro entre 2 e 256)"
        )

    height, width = image_gray.shape
    out = np.zeros((height, width), dtype=np.uint8)
    step = 256.0 / levels

    for y in range(height):
        for x in range(width):
            value = int(image_gray[y, x])
            bucket = int(value / step)
            if bucket >= levels:
                bucket = levels - 1
            representative = (bucket + 0.5) * step
            out[y, x] = _saturate_round(representative)

    return out


def _saturate_round(value: float) -> int:
    """Arredonda e satura um valor real para o intervalo [0, 255]."""

    rounded = int(round(value))
    if rounded < 0:
        return 0
    if rounded > 255:
        return 255
    return rounded
