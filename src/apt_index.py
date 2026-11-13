"""Чтение индекса Ubuntu Packages средствами стандартной библиотеки."""

from dataclasses import dataclass
import gzip
import lzma
import re
from urllib.parse import urlsplit
from urllib.request import urlopen

TIMEOUT = 30
TERM = re.compile(
    r"([a-z0-9][a-z0-9+.-]*)(?::[a-z0-9-]+)?"
    r"(?:\s*\((<<|<=|=|>=|>>)\s*([A-Za-z0-9.+:~\-]+)\))?"
)


@dataclass(frozen=True)
class Requirement:
    """Имя зависимости и необязательное ограничение версии."""

    name: str
    operator: str | None = None
    version: str | None = None

    def __str__(self):
        """Показать требование в синтаксисе APT."""
        if self.operator:
            return f"{self.name} ({self.operator} {self.version})"
        return self.name


@dataclass(frozen=True)
class Release:
    """Пакет конкретной версии и его метаданные."""

    name: str
    version: str
    groups: tuple
    provides: tuple


def records(text):
    """Разобрать разделённые пустыми строками записи индекса."""
    fields = {}
    last_key = None
    for line in text.splitlines():
        if not line.strip():
            if fields:
                yield fields
            fields, last_key = {}, None
        elif line[0].isspace() and last_key:
            fields[last_key] += " " + line.strip()
        else:
            key, separator, value = line.partition(":")
            if separator:
                fields[key] = value.strip()
                last_key = key
    if fields:
        yield fields


def parse_group(value):
    """Прочитать одно требование с возможными альтернативами."""
    result = []
    for part in value.split("|"):
        match = TERM.fullmatch(part.strip())
        if not match:
            raise ValueError(f"Неизвестный синтаксис зависимости: {part}")
        result.append(Requirement(*match.groups()))
    return tuple(result)


def dependency_groups(value):
    """Разбить перечисление APT на обязательные группы."""
    return tuple(parse_group(group) for group in value.split(",")
                 if group.strip())


def read_index(text):
    """Собрать пакетные записи по имени, включая несколько версий."""
    packages = {}
    for row in records(text):
        if not {"Package", "Version"} <= row.keys():
            continue
        groups = dependency_groups(row.get("Pre-Depends", ""))
        groups += dependency_groups(row.get("Depends", ""))
        provides = tuple(group[0] for group in
                         dependency_groups(row.get("Provides", "")))
        release = Release(row["Package"], row["Version"], groups, provides)
        packages.setdefault(release.name, {})[release.version] = release
    if not packages:
        raise ValueError("В индексе Packages нет записей о пакетах")
    return packages


def download_index(url):
    """Загрузить обычный, gzip или xz индекс Packages по URL."""
    with urlopen(url, timeout=TIMEOUT) as response:
        data = response.read()
    path = urlsplit(url).path
    if path.endswith(".xz"):
        data = lzma.decompress(data)
    elif path.endswith(".gz"):
        data = gzip.decompress(data)
    return read_index(data.decode("utf-8"))


def exact_release(packages, name, version):
    """Найти ровно указанную версию корневого пакета."""
    if name not in packages:
        raise ValueError(f"Пакет {name} не найден в индексе")
    if version not in packages[name]:
        available = ", ".join(sorted(packages[name]))
        raise ValueError(f"{name}: нет версии {version}; доступны {available}")
    return packages[name][version]
