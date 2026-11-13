"""CLI инструмента анализа зависимостей Ubuntu."""

import argparse
import csv
import lzma
from pathlib import Path

from apt_index import download_index, exact_release
from config import load_config

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "examples/hello.csv"


def main():
    """Получить прямые зависимости из указанного индекса Ubuntu."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if config.test_mode:
            raise ValueError("Тестовый граф будет поддержан на этапе 3")
        packages = download_index(config.repository)
        release = exact_release(packages, config.package, config.version)
        print(f"{release.name} {release.version}:")
        for group in release.groups:
            print(" | ".join(map(str, group)))
        if not release.groups:
            print("Нет прямых зависимостей")
    except (ValueError, OSError, csv.Error, lzma.LZMAError) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
