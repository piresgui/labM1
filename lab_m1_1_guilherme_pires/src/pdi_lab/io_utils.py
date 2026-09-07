"""Funcoes auxiliares de entrada/saida de imagens.

Estas funcoes usam Pillow apenas para abrir/salvar arquivos e criar arrays
numpy. Nenhuma operacao avaliada (copia, separacao de canais, conversao para
cinza, quantizacao) e feita aqui.
"""

from __future__ import annotations

import os

import numpy as np
from PIL import Image, UnidentifiedImageError


class ImageLoadError(RuntimeError):
    """Erro ao carregar uma imagem de entrada."""


def load_image_rgb(path: str) -> np.ndarray:
    """Abre uma imagem e devolve um array numpy uint8 no modo RGB (H, W, 3).

    Sempre convertemos explicitamente para RGB para que o restante do
    programa possa assumir uma convencao fixa de canais (R, G, B nessa
    ordem), independente do modo original do arquivo (L, P, RGBA, CMYK...).
    """

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
    """Resolve o caminho de saida: se `output` for um diretorio (ou terminar
    com separador), usa `default_name` dentro dele; senao usa `output` como
    caminho de arquivo direto."""

    if output.endswith(("/", "\\")) or os.path.isdir(output):
        return os.path.join(output, default_name)
    return output
