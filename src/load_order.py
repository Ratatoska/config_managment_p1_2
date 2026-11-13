"""Порядок зависимостей: сначала потомки, затем пакет."""

from dataclasses import dataclass


@dataclass
class LoadOrder:
    """Список пакетов и обнаруженные циклы."""

    packages: list
    cycles: list


def load_order(graph):
    """Обойти граф итеративно, не зависая на циклическом ребре."""
    result = LoadOrder([], [])
    done, active, path = set(), set(), []
    stack = [(next(iter(graph.edges)), False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            path.pop()
            active.remove(node)
            done.add(node)
            result.packages.append(node)
        elif node in active:
            result.cycles.append((*path[path.index(node):], node))
        elif node not in done:
            path.append(node)
            active.add(node)
            stack.append((node, True))
            for child in reversed(graph.edges[node]):
                stack.append((child, False))
    return result


def print_order(graph):
    """Показать порядок либо пояснить, что цикл мешает строгому порядку."""
    result = load_order(graph)
    if result.cycles:
        print('Есть циклы: строгий порядок невозможен.')
        for cycle in result.cycles:
            print('Цикл: ' + ' -> '.join(map(str, cycle)))
        print('Порядок после пропуска обратных рёбер:')
    for number, node in enumerate(result.packages, 1):
        print(f'{number}. {node}')
