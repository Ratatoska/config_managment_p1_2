"""Два источника рёбер: индекс APT и учебный текстовый файл."""

from dataclasses import dataclass
from pathlib import Path
import re

from apt_index import download_index, exact_release
from debian_version import satisfies, version_key

TEST_NAME = re.compile(r"[A-Z]+")


@dataclass(frozen=True)
class Package:
    """Узел графа: имя и выбранная версия, если она известна."""

    name: str
    version: str = ""

    def __str__(self):
        """Версия отображается только там, где она известна."""
        return f"{self.name} {self.version}" if self.version else self.name


def test_graph(path):
    """Прочитать строки вида A: B C, проверить ссылки и повторы."""
    graph = {}
    for number, raw in enumerate(path.read_text("utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        name, colon, tail = line.partition(":")
        name = name.strip()
        children = tail.split()
        if not colon or not all(map(TEST_NAME.fullmatch, [name, *children])):
            raise ValueError(f"Строка {number}: ожидается запись вида A: B C")
        if name in graph:
            raise ValueError(f"Строка {number}: повтор пакета {name}")
        graph[name] = tuple(dict.fromkeys(children))
    undefined = {child for items in graph.values() for child in items}
    undefined -= graph.keys()
    if undefined:
        raise ValueError("Не описаны пакеты: " + ", ".join(sorted(undefined)))
    return graph


def from_test(config):
    """Вернуть начальный узел и способ чтения его соседей."""
    graph = test_graph(Path(config.repository))
    if config.package not in graph:
        raise ValueError(f"Пакет {config.package} не найден в тестовом файле")

    def neighbors(node):
        """Вернуть соседей тестового пакета."""
        return tuple(Package(name) for name in graph[node.name])

    return Package(config.package), neighbors


def providers(packages):
    """Построить справочник виртуальных пакетов из Provides."""
    found = {}
    for versions in packages.values():
        for release in versions.values():
            for term in release.provides:
                found.setdefault(term.name, []).append((release, term.version))
    return found


def pick_release(group, packages, virtual):
    """Выбрать первую доступную альтернативу, предпочитая прямое имя."""
    for term in group:
        versions = packages.get(term.name, {})
        matching = [release for release in versions.values()
                    if satisfies(release.version, term)]
        if matching:
            return max(matching, key=lambda item: version_key(item.version))
        matching = [release for release, version in virtual.get(term.name, ())
                    if satisfies(version, term)]
        if matching:
            return min(matching, key=lambda item: item.name)
    return None


def from_apt(config):
    """Загрузить индекс один раз и вернуть корневой пакет и соседей."""
    packages = download_index(config.repository)
    root = exact_release(packages, config.package, config.version)
    virtual = providers(packages)

    def neighbors(node):
        """Превратить требования версии в выбранные узлы."""
        if not node.version:
            return ()
        release = packages[node.name][node.version]
        result = []
        for group in release.groups:
            child = pick_release(group, packages, virtual)
            if child:
                result.append(Package(child.name, child.version))
            else:
                result.append(Package(" | ".join(map(str, group))))
        return tuple(dict.fromkeys(result))

    return Package(root.name, root.version), neighbors
