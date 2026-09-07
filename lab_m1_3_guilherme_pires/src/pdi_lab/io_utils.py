"""Funcoes auxiliares de entrada/saida de imagens e kernels.

Pillow e usado apenas para abrir/salvar arquivos e criar arrays numpy.
"""

from __future__ import annotations

import os

import numpy as np
from PIL import Image, UnidentifiedImageError


class ImageLoadError(RuntimeError):
    """Erro ao carregar uma imagem de entrada."""


class KernelError(ValueError):
    """Erro ao carregar ou validar um kernel."""


def load_image_gray(path: str) -> np.ndarray:
    """Abre uma imagem e devolve um array numpy uint8 em niveis de cinza
    (H, W), convertendo com a media ponderada manual."""

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

    from .ops import grayscale_weighted  # import local para evitar ciclo

    return grayscale_weighted(array)


def save_image(path: str, array: np.ndarray) -> None:
    """Salva um array numpy (H, W) uint8 como arquivo de imagem em niveis
    de cinza."""

    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if array.dtype != np.uint8:
        raise ValueError("a imagem de saida deve estar em uint8 (pos-saturacao)")

    if array.ndim != 2:
        raise ValueError(f"formato de array nao suportado para salvar: {array.shape}")

    Image.fromarray(array, mode="L").save(path)


def resolve_output_path(output: str, default_name: str) -> str:
    if output.endswith(("/", "\\")) or os.path.isdir(output):
        return os.path.join(output, default_name)
    return output


def load_kernel(path: str) -> np.ndarray:
    """Carrega um kernel de um arquivo de texto no formato:

        linhas colunas
        v11 v12 ... v1c
        v21 v22 ... v2c
        ...

    Valida existencia do arquivo, quantidade correta de valores, forma
    quadrada e dimensao impar.
    """

    if not os.path.isfile(path):
        raise KernelError(f"arquivo de kernel nao encontrado: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        tokens = fh.read().split()

    if len(tokens) < 2:
        raise KernelError(f"kernel vazio ou mal formatado: {path}")

    try:
        rows = int(tokens[0])
        cols = int(tokens[1])
    except ValueError as exc:
        raise KernelError(f"cabecalho do kernel invalido em {path}") from exc

    if rows <= 0 or cols <= 0:
        raise KernelError(f"dimensoes do kernel invalidas: {rows}x{cols}")

    values = tokens[2:]
    expected = rows * cols
    if len(values) != expected:
        raise KernelError(
            f"quantidade de valores incorreta no kernel: esperado {expected}, "
            f"encontrado {len(values)}"
        )

    try:
        numbers = [float(v) for v in values]
    except ValueError as exc:
        raise KernelError(f"valor nao numerico no kernel {path}") from exc

    kernel = np.array(numbers, dtype=np.float64).reshape(rows, cols)
    validate_kernel(kernel)
    return kernel


def validate_kernel(kernel: np.ndarray) -> None:
    """Valida que o kernel e nao vazio, quadrado e de dimensao impar."""

    if kernel.size == 0:
        raise KernelError("kernel vazio")

    if kernel.ndim != 2:
        raise KernelError("kernel deve ser uma matriz 2D")

    rows, cols = kernel.shape
    if rows != cols:
        raise KernelError(f"kernel nao e quadrado: {rows}x{cols}")

    if rows % 2 == 0:
        raise KernelError(f"kernel de dimensao par nao permitido: {rows}x{cols}")
