"""CLI инструмента анализа зависимостей Ubuntu."""

import argparse
import csv
from dataclasses import asdict
from pathlib import Path

from config import load_config

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "examples/diamond.csv"


def main():
    """Загрузить CSV и вывести настройки прототипа."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        for key, value in asdict(load_config(args.config)).items():
            print(f"{key} = {value}")
    except (ValueError, OSError, csv.Error) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
