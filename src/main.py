"""CLI инструмента анализа зависимостей Ubuntu."""

import argparse
import csv
import lzma
from pathlib import Path
from subprocess import TimeoutExpired
from xml.etree.ElementTree import ParseError

from config import load_config
from graph import build_graph, print_graph
from load_order import print_order
from repository import from_apt, from_test
from visual import render_svg

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "examples/diamond.csv"


def main():
    """Построить граф для выбранного источника данных."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--load-order', action='store_true',
                       help='показать зависимости перед пакетами')
    modes.add_argument('--svg', action='store_true',
                       help='записать PlantUML и SVG')
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        source = from_test if config.test_mode else from_apt
        root, neighbors = source(config)
        graph = build_graph(root, neighbors, config.max_depth, config.exclude)
        if args.load_order:
            print_order(graph)
        elif args.svg:
            render_svg(graph, config.output)
            print(f'SVG: {config.output}')
        else:
            print_graph(graph)
    except (ValueError, OSError, csv.Error, lzma.LZMAError, TimeoutExpired,
            ParseError) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
