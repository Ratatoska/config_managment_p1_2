# Практическая работа № 2. Граф зависимостей Ubuntu

**Вариант 8 · Комаров В.Ю. · ИКБО-41-25**

Этап 4: к графу добавлен вывод порядка зависимостей. Если есть цикл,
программа показывает его и сообщает, что строгого порядка не существует.
Нужен Python 3.10+, сторонних библиотек нет.

```bash
python -X utf8 src/main.py examples/hello.csv
python -X utf8 src/main.py examples/diamond.csv
python -X utf8 src/main.py examples/cycle.csv
python -X utf8 src/main.py examples/filtered.csv
python -X utf8 src/main.py examples/diamond.csv --load-order
python -X utf8 src/main.py examples/cycle.csv --load-order
python -m unittest discover -s tests -v
```

CSV без заголовка: одна строка `ключ,значение` на параметр.
Пути к локальным файлам отсчитываются от каталога CSV. Тесты проверяют
корректный пример и сообщения об ошибках всех семи параметров.

[Сравнение порядка с APT](docs/apt-comparison.md).
