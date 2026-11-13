"""Сравнение версий Debian: epoch, основная версия, ревизия."""

import re
from functools import cmp_to_key

TILDE_ORDER = -1
OTHER_ORDER = 256


def order(char):
    """Тильда раньше конца, буквы раньше прочих знаков."""
    if char == "~":
        return TILDE_ORDER
    if not char or char.isdigit():
        return 0
    return ord(char) if char.isalpha() else ord(char) + OTHER_ORDER


def parts(version):
    """Пустые epoch и Debian revision означают ноль."""
    epoch, sep, rest = version.partition(":")
    if not sep:
        epoch, rest = "0", epoch
    upstream, dash, revision = rest.rpartition("-")
    return (int(epoch), upstream, revision) if dash else (int(epoch), rest, "0")


def compare_text(left, right):
    """Сравнить попеременно нечисловые символы и целые числа."""
    while left or right:
        left, right, difference = compare_prefix(left, right)
        if difference:
            return difference
        a = re.match(r"[0-9]*", left).group()
        b = re.match(r"[0-9]*", right).group()
        if int(a or "0") != int(b or "0"):
            return int(a or "0") - int(b or "0")
        left, right = left[len(a):], right[len(b):]
    return 0


def compare_prefix(left, right):
    """Сравнить нечисловой префикс и вернуть оставшиеся суффиксы."""
    while (left and not left[0].isdigit()
           or right and not right[0].isdigit()):
        a, b = order(left[:1]), order(right[:1])
        if a != b:
            return left, right, a - b
        left, right = left[1:], right[1:]
    return left, right, 0


def compare(left, right):
    """Вернуть отрицательное число, ноль или положительное число."""
    a, b = parts(left), parts(right)
    return a[0] - b[0] or compare_text(a[1], b[1]) or compare_text(a[2], b[2])


version_key = cmp_to_key(compare)


def satisfies(version, term):
    """Проверить требование Depends к конкретной версии."""
    if not term.operator:
        return True
    if not version:
        return False
    diff = compare(version, term.version)
    return {"<<": diff < 0, "<=": diff <= 0, "=": diff == 0,
            ">=": diff >= 0, ">>": diff > 0}[term.operator]
