"""Прочитать и проверить семь параметров CSV."""

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

PACKAGE = r"[a-z0-9][a-z0-9+.-]*"
TEST_PACKAGE = r"[A-Z]+"
VERSION = r"(?:[0-9]+:)?[0-9][A-Za-z0-9.+~\-]*"
FIELDS = {"package", "repository", "test_mode", "version",
          "output", "max_depth", "exclude"}
ROW_SIZE = 2
MAX_DEPTH = 100
CONTROL_CHAR = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class Config:
    """Проверенные настройки одного запуска."""

    package: str
    repository: str
    test_mode: bool
    version: str
    output: Path
    max_depth: int
    exclude: str


def read_rows(path):
    """Считать CSV без заголовка: по одной паре ключ,значение на строку."""
    values = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for number, row in enumerate(csv.reader(stream, strict=True), 1):
            if not row:
                continue
            if len(row) != ROW_SIZE:
                raise ValueError(f"CSV, строка {number}: нужно два поля")
            key, value = (field.strip() for field in row)
            if key not in FIELDS or key in values:
                raise ValueError(f"CSV: неизвестный или повторный ключ {key!r}")
            if CONTROL_CHAR.search(value):
                raise ValueError(f"{key}: управляющий символ в значении")
            values[key] = value
    missing = FIELDS - values.keys()
    if missing:
        raise ValueError("CSV: отсутствуют " + ", ".join(sorted(missing)))
    return values


def repository_path(value, test_mode, base):
    """Проверить путь к тестовому файлу или сетевой адрес индекса."""
    if test_mode:
        path = (base / value).resolve()
        if not path.is_file():
            raise ValueError(f"repository: файл не найден: {path}")
        return str(path)
    url = urlsplit(value)
    if not (url.scheme in {"http", "https"} and url.hostname
            and url.username is None and not any(map(str.isspace, value))):
        raise ValueError("repository: нужен URL HTTP или HTTPS")
    return value


def load_config(path):
    """Проверить имена, путь, режим, версию, глубину, фильтр и выход."""
    path = path.resolve()
    data = read_rows(path)
    mode = data["test_mode"].lower()
    if mode not in {"true", "false"}:
        raise ValueError("test_mode: укажите true или false")
    test_mode = mode == "true"
    pattern = TEST_PACKAGE if test_mode else PACKAGE
    if not re.fullmatch(pattern, data["package"]):
        raise ValueError("package: неверное имя пакета для выбранного режима")
    if not re.fullmatch(VERSION, data["version"]):
        raise ValueError("version: неверная версия пакета")
    output = (path.parent / data["output"]).resolve()
    if output.suffix.lower() != ".svg" or output.is_dir():
        raise ValueError("output: укажите путь к файлу .svg")
    if data["exclude"] and not re.fullmatch(
        r"[A-Za-z0-9.+-]+", data["exclude"]
    ):
        raise ValueError("exclude: допустимы буквы, цифры, точки, плюс и дефис")
    repository = repository_path(data["repository"], test_mode, path.parent)
    return Config(data["package"], repository, test_mode, data["version"],
                  output, parse_depth(data["max_depth"]), data["exclude"])


def parse_depth(value):
    """Проверить число уровней и ограничить глубину рекурсии."""
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError("max_depth: нужно целое неотрицательное число")
    depth = int(value)
    if depth > MAX_DEPTH:
        raise ValueError(f"max_depth: допустимо до {MAX_DEPTH}")
    return depth
