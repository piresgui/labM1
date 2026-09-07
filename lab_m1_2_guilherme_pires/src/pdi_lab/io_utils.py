"""Funcoes auxiliares de entrada/saida de imagens.

Pillow e usado apenas para abrir/salvar arquivos e criar arrays numpy.
"""

from __future__ import annotations

import os

import numpy as np
from PIL import Image, UnidentifiedImageError


class ImageLoadError(RuntimeError):
    """Erro ao carregar uma imagem de entrada."""


def load_image_rgb(path: str) -> np.ndarray:
    """Abre uma imagem e devolve um array numpy uint8 no modo RGB (H, W, 3)."""

    if not os.path.isfile(path):
        raise ImageLoadError(f"arquivo de entrada nao encontrado: {path}")

    try:
        with Image.open(path) as img:
            img_rgb = img.convert("RGB")
            array = np.array(img_rgb, dtype=np.uint8)
    except UnidentifiedImageError as exc:
        raise ImageLoadError(f"falha ao abrir imagem: {path} ({exc})") from exc
    except OSError as exc:
        raise ImageLoadError(f"falha ao ler imagem: {path} ({exc})") from exc

    if array.ndim != 3 or array.shape[2] != 3:
        raise ImageLoadError(
            f"numero inesperado de canais apos conversao para RGB: {array.shape}"
        )

    return array


def load_image_gray(path: str) -> np.ndarray:
    """Abre uma imagem e devolve um array numpy uint8 em niveis de cinza
    (H, W), convertendo com a media ponderada manual (nao usa img.convert('L'),
    que aplicaria a conversao pronta da biblioteca)."""

    from .ops import grayscale_weighted  # import local para evitar ciclo

    rgb = load_image_rgb(path)
    return grayscale_weighted(rgb)


def save_image(path: str, array: np.ndarray) -> None:
    """Salva um array numpy (H, W) ou (H, W, 3) uint8 como arquivo de imagem."""

    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if array.dtype != np.uint8:
        raise ValueError("a imagem de saida deve estar em uint8 (pos-saturacao)")

    if array.ndim == 2:
        mode = "L"
    elif array.ndim == 3 and array.shape[2] == 3:
        mode = "RGB"
    else:
        raise ValueError(f"formato de array nao suportado para salvar: {array.shape}")

    Image.fromarray(array, mode=mode).save(path)


def resolve_output_path(output: str, default_name: str) -> str:
    if output.endswith(("/", "\\")) or os.path.isdir(output):
        return os.path.join(output, default_name)
    return output
