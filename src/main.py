"""CLI инструмента анализа зависимостей Ubuntu."""

import argparse
import csv
import lzma
from pathlib import Path

from config import load_config
from graph import build_graph, print_graph
from repository import from_apt, from_test

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "examples/diamond.csv"


def main():
    """Построить граф для выбранного источника данных."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        source = from_test if config.test_mode else from_apt
        root, neighbors = source(config)
        graph = build_graph(root, neighbors, config.max_depth, config.exclude)
        print_graph(graph)
    except (ValueError, OSError, csv.Error, lzma.LZMAError) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
