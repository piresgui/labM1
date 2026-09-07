"""Interface de linha de comando do Laboratorio M1.1.

Uso:
    python -m pdi_lab --input <arq> --output <arq_ou_dir> --operation <op> [--levels N]
"""

from __future__ import annotations

import argparse
import sys

from . import ops
from .io_utils import ImageLoadError, load_image_rgb, resolve_output_path, save_image

OPERATIONS = [
    "inspect",
    "copy",
    "channel_b",
    "channel_g",
    "channel_r",
    "grayscale_average",
    "grayscale_weighted",
    "quantize",
]

_DEFAULT_NAMES = {
    "copy": "copy.png",
    "channel_b": "channel_b.png",
    "channel_g": "channel_g.png",
    "channel_r": "channel_r.png",
    "grayscale_average": "gray_average.png",
    "grayscale_weighted": "gray_weighted.png",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description="Laboratorio M1.1 - representacao, canais e niveis de cinza.",
    )
    parser.add_argument("--input", required=True, help="imagem de entrada")
    parser.add_argument("--output", required=True, help="arquivo ou diretorio de saida")
    parser.add_argument(
        "--operation", required=True, choices=OPERATIONS, help="operacao a executar"
    )
    parser.add_argument(
        "--levels", type=int, default=None, help="quantidade de niveis para quantize"
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

    try:
        return _run_operation(args, image_rgb)
    except ops.OperationError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1


def _run_operation(args: argparse.Namespace, image_rgb) -> int:
    operation = args.operation

    if operation == "inspect":
        stats = ops.inspect(image_rgb)
        print(f"width={stats['width']}")
        print(f"height={stats['height']}")
        print(f"channels={stats['channels']}")
        print(f"pixels={stats['pixels']}")
        print(f"type={stats['dtype']}")
        print(f"min={stats['min']}")
        print(f"max={stats['max']}")
        print(f"mean={stats['mean']:.4f}")
        names = ["r", "g", "b"]
        for i, name in enumerate(names):
            print(
                f"channel_{name}_min={stats['channel_min'][i]} "
                f"channel_{name}_max={stats['channel_max'][i]} "
                f"channel_{name}_mean={stats['channel_mean'][i]:.4f}"
            )
        return 0

    if operation == "copy":
        result = ops.copy_manual(image_rgb)
        out_path = resolve_output_path(args.output, _DEFAULT_NAMES[operation])
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation in ("channel_b", "channel_g", "channel_r"):
        channel = operation.split("_")[1]
        result = ops.channel_isolate(image_rgb, channel)
        out_path = resolve_output_path(args.output, _DEFAULT_NAMES[operation])
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "grayscale_average":
        result = ops.grayscale_average(image_rgb)
        out_path = resolve_output_path(args.output, _DEFAULT_NAMES[operation])
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "grayscale_weighted":
        result = ops.grayscale_weighted(image_rgb)
        out_path = resolve_output_path(args.output, _DEFAULT_NAMES[operation])
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    if operation == "quantize":
        if args.levels is None:
            raise ops.OperationError("--levels e obrigatorio para a operacao quantize")
        gray = ops.grayscale_weighted(image_rgb)
        result = ops.quantize(gray, args.levels)
        default_name = f"quant_{args.levels}.png"
        out_path = resolve_output_path(args.output, default_name)
        save_image(out_path, result)
        print(f"saida gravada em {out_path}")
        return 0

    raise ops.OperationError(f"operacao desconhecida: {operation}")


if __name__ == "__main__":
    sys.exit(main())
