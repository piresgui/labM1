"""Interface de linha de comando do Laboratorio M1.2.

Uso:
    python -m pdi_lab --input <arq> --output <arq_ou_dir> --operation <op> \
        [--value N] [--alpha A] [--threshold T]
"""

from __future__ import annotations

import argparse
import csv
import os
import sys

from . import ops
from .io_utils import ImageLoadError, load_image_rgb, resolve_output_path, save_image

OPERATIONS = ["brightness", "contrast", "negative", "threshold", "histogram"]

_DEFAULT_NAMES = {
    "negative": "negative.png",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description="Laboratorio M1.2 - transformacoes de intensidade.",
    )
    parser.add_argument("--input", required=True, help="imagem de entrada")
    parser.add_argument("--output", required=True, help="arquivo ou diretorio de saida")
    parser.add_argument(
        "--operation", required=True, choices=OPERATIONS, help="operacao a executar"
    )
    parser.add_argument("--value", type=float, default=None, help="valor de brilho (b)")
    parser.add_argument("--alpha", type=float, default=None, help="fator de contraste")
    parser.add_argument(
        "--threshold", type=float, default=None, help="limiar T para binarizacao"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        image_rgb = load_image_rgb(args.input)
    except ImageLoadError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    gray = ops.grayscale_weighted(image_rgb)

    try:
        return _run_operation(args, gray)
    except ops.OperationError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1


def _run_operation(args: argparse.Namespace, gray) -> int:
    operation = args.operation

    if operation == "brightness":
        if args.value is None:
            raise ops.OperationError("--value e obrigatorio para a operacao brightness")
        result = ops.brightness(gray, args.value)
        out_path = resolve_output_path(args.output, "brightness.png")
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "contrast":
        if args.alpha is None:
            raise ops.OperationError("--alpha e obrigatorio para a operacao contrast")
        result = ops.contrast(gray, args.alpha)
        out_path = resolve_output_path(args.output, "contrast.png")
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "negative":
        result = ops.negative(gray)
        out_path = resolve_output_path(args.output, _DEFAULT_NAMES[operation])
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "threshold":
        if args.threshold is None:
            raise ops.OperationError(
                "--threshold e obrigatorio para a operacao threshold"
            )
        result = ops.threshold(gray, args.threshold)
        out_path = resolve_output_path(args.output, "threshold.png")
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "histogram":
        counts = ops.histogram(gray)
        out_path = resolve_output_path(args.output, "histogram.csv")
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["intensity", "count"])
            for intensity, count in enumerate(counts):
                writer.writerow([intensity, count])
        print(f"saida gravada em {out_path}")
        return 0

    raise ops.OperationError(f"operacao desconhecida: {operation}")


if __name__ == "__main__":
    sys.exit(main())
