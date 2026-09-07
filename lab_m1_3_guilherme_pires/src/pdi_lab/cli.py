"""Interface de linha de comando do Laboratorio M1.3.

Uso:
    python -m pdi_lab --input <arq> --output <arq_ou_dir> --operation <op> \
        [--kernel <arq>] [--border copy|replicate]
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

from . import ops
from .io_utils import (
    ImageLoadError,
    KernelError,
    load_image_gray,
    load_kernel,
    resolve_output_path,
    save_image,
)

OPERATIONS = ["convolution", "mean_filter", "weighted_mean", "laplacian", "sobel"]

DEFAULT_BORDER = "replicate"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description="Laboratorio M1.3 - convolucao e filtragem espacial.",
    )
    parser.add_argument("--input", required=True, help="imagem de entrada")
    parser.add_argument("--output", required=True, help="arquivo ou diretorio de saida")
    parser.add_argument(
        "--operation", required=True, choices=OPERATIONS, help="operacao a executar"
    )
    parser.add_argument("--kernel", default=None, help="arquivo de kernel (formato do contrato)")
    parser.add_argument(
        "--border",
        default=DEFAULT_BORDER,
        choices=list(ops.BORDER_STRATEGIES),
        help="estrategia de tratamento de borda",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        gray = load_image_gray(args.input)
    except ImageLoadError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    try:
        return _run_operation(args, gray)
    except (ops.OperationError, KernelError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1


def _split_output(output: str, default_stem: str) -> tuple[str, str]:
    """Retorna (diretorio, stem-sem-extensao) para gerar multiplos arquivos
    de saida a partir de um unico --output (arquivo ou diretorio)."""

    if output.endswith(("/", "\\")) or os.path.isdir(output):
        return output, default_stem

    directory = os.path.dirname(output) or "."
    stem = os.path.splitext(os.path.basename(output))[0]
    return directory, stem


def _run_operation(args: argparse.Namespace, gray: np.ndarray) -> int:
    operation = args.operation

    if operation == "convolution":
        if not args.kernel:
            raise ops.OperationError("--kernel e obrigatorio para a operacao convolution")
        kernel = load_kernel(args.kernel)
        response = ops.convolve(gray, kernel, args.border)
        result = ops.to_uint8(response)
        out_path = resolve_output_path(args.output, "convolution.png")
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "mean_filter":
        if args.kernel:
            kernel = load_kernel(args.kernel)
            response = ops.convolve(gray, kernel, args.border)
            result = ops.to_uint8(response)
        else:
            result = ops.mean_filter(gray, args.border)
        out_path = resolve_output_path(args.output, "mean_filter.png")
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "weighted_mean":
        result = ops.weighted_mean_filter(gray, args.border)
        out_path = resolve_output_path(args.output, "weighted_mean.png")
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "laplacian":
        result = ops.laplacian(gray, args.border)
        directory, stem = _split_output(args.output, "laplacian")
        vis_path = os.path.join(directory, f"{stem}.png")
        enhanced_path = os.path.join(directory, f"{stem}_enhanced.png")
        save_image(vis_path, result["visualization"])
        save_image(enhanced_path, result["enhanced"])
        print(f"saida gravada em {vis_path}")
        print(f"saida gravada em {enhanced_path}")
        return 0

    if operation == "sobel":
        result = ops.sobel(gray, args.border)
        directory, stem = _split_output(args.output, "sobel")
        gx_path = os.path.join(directory, f"{stem}_gx.png")
        gy_path = os.path.join(directory, f"{stem}_gy.png")
        mag_approx_path = os.path.join(directory, f"{stem}_magnitude_approx.png")
        mag_euclid_path = os.path.join(directory, f"{stem}_magnitude_euclidean.png")
        save_image(gx_path, result["gx"])
        save_image(gy_path, result["gy"])
        save_image(mag_approx_path, result["magnitude_approx"])
        save_image(mag_euclid_path, result["magnitude_euclidean"])
        for p in (gx_path, gy_path, mag_approx_path, mag_euclid_path):
            print(f"saida gravada em {p}")
        return 0

    raise ops.OperationError(f"operacao desconhecida: {operation}")


if __name__ == "__main__":
    sys.exit(main())
