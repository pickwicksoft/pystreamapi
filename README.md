![Header](https://raw.githubusercontent.com/PickwickSoft/pystreamapi/main/assets/header.png)

<h1 align="center">PyStreamAPI</h1>

<p align="center">
  <a href="https://deepsource.io/gh/PickwickSoft/pystreamapi/?ref=repository-badge"><img src="https://deepsource.io/gh/PickwickSoft/pystreamapi.svg/?label=active+issues&show_trend=true&token=7lV9pH1U-N1oId03M-XKZL5B"  alt="DeepSource"/></a>
  <a href="https://github.com/PickwickSoft/pystreamapi/actions/workflows/unittests.yml"><img src="https://github.com/PickwickSoft/pystreamapi/actions/workflows/unittests.yml/badge.svg"  alt="Tests"/></a>
  <a href="https://github.com/PickwickSoft/pystreamapi/actions/workflows/pylint.yml"><img src="https://github.com/PickwickSoft/pystreamapi/actions/workflows/pylint.yml/badge.svg"  alt="Pylint"/></a>
  <a href="https://sonarcloud.io/summary/new_code?id=PickwickSoft_pystreamapi"><img src="https://sonarcloud.io/api/project_badges/measure?project=PickwickSoft_pystreamapi&metric=alert_status"  alt="Quality Gate"/></a>
  <a href="https://sonarcloud.io/summary/new_code?id=PickwickSoft_pystreamapi"><img src="https://sonarcloud.io/api/project_badges/measure?project=PickwickSoft_pystreamapi&metric=coverage"  alt="Coverage"/></a>
  <a href="https://pypi.org/project/streams-py/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/streams.py"></a>
  <a href="https://pypi.org/project/streams-py/"><img alt="PyPI" src="https://img.shields.io/pypi/v/streams.py"></a>
</p>

PyStreamAPI is a Python stream library inspired by the Java Stream API, adding Pythonic features for clean, declarative, and efficient data processing. It supports both sequential and parallel streams with lazy evaluation.

```python
from pystreamapi import Stream

Stream.of([" ", '3', None, "2", 1, ""]) \
    .filter(lambda x: x is not None) \
    .map(str) \
    .map(lambda x: x.strip()) \
    .filter(lambda x: len(x) > 0) \
    .map(int) \
    .sorted() \
    .for_each(print) # Output: 1 2 3
```

## Installation

```bash
pip install streams.py
```

```python
from pystreamapi import Stream
```

:tada: PyStreamAPI is now ready to process your data

## Why PyStreamAPI?

* Sequential and parallel streams out of the box
* Lazy execution for efficient processing of large datasets
* 100% test coverage
* Pythonic API — clean, readable, and expressive
* 111+ built-in [conditions](https://pystreamapi.pickwicksoft.org/reference/conditions) for filtering and matching
* Declarative [error handling](https://pystreamapi.pickwicksoft.org/reference/api-reference/error-handling) with configurable error levels
* Built-in loaders for CSV, JSON, XML, YAML and TOML files

## Building a Stream

PyStreamAPI provides two stream types — `Stream` (general-purpose) and `NumericStream` (for numerical data with statistics) — each available in sequential and parallel flavors.

```python
Stream.of([1, 2, 3])               # auto-selects sequential or numeric
Stream.parallel_of([1, 2, 3])      # parallel stream
Stream.sequential_of([1, 2, 3])    # sequential stream
Stream.of_noneable(None)           # returns empty stream when source is None
Stream.iterate(0, lambda n: n + 2) # infinite stream (use .limit())
Stream.concat(Stream.of([1, 2]), Stream.of([3, 4]))  # merge streams
```

For the full API reference see the [docs](https://pystreamapi.pickwicksoft.org/quick-start).

## Conditions

![Conditions](https://raw.githubusercontent.com/PickwickSoft/pystreamapi/main/assets/conditions.png)

Over 111 ready-to-use conditions across strings, numbers, types, and dates — combine them freely with `one_of()`:

```python
from pystreamapi import Stream
from pystreamapi.conditions import prime, even, one_of

Stream.of([1, 2, 3, 4, 5]) \
    .filter(one_of(even(), prime())) \
    .for_each(print) # 2, 3, 4, 5
```

## Error Handling

Control error behavior per-operation with `error_level()`:

```python
from pystreamapi import Stream, ErrorLevel

Stream.of([" ", '3', None, "2", 1, ""]) \
    .error_level(ErrorLevel.IGNORE) \
    .map_to_int() \
    .sorted() \
    .for_each(print) # Output: 1 2 3
```

Available levels: `RAISE` (default), `IGNORE`, `WARN`. See the [error handling docs](https://pystreamapi.pickwicksoft.org/reference/api-reference/error-handling) for details.

## Data Loaders

Load data from files directly into a stream — no manual parsing needed:

| Loader | Install | Description |
|--------|---------|-------------|
| `csv`  | core    | CSV files with optional type casting and delimiter |
| `json` | `pip install 'streams.py[json_loader]'` | JSON files or strings (streaming via ijson) |
| `xml`  | `pip install 'streams.py[xml_loader]'` | XML files or strings with node path access |
| `yaml` | core    | YAML files or strings |
| `toml` | core    | TOML files or strings |

```python
from pystreamapi import Stream
from pystreamapi.loaders import csv

Stream.of(csv("data.csv", delimiter=";")) \
    .map(lambda x: x.name) \
    .for_each(print)
```

Install all optional extras at once: `pip install 'streams.py[all]'`

See the [data loaders docs](https://pystreamapi.pickwicksoft.org/reference/data-loaders) for full usage.

## Documentation

Full documentation: [pystreamapi.pickwicksoft.org](https://pystreamapi.pickwicksoft.org/)

## Bug Reports

Bug reports can be submitted in GitHub's [issue tracker](https://github.com/PickwickSoft/pystreamapi/issues).

## Contributing

Contributions are welcome! Please submit a pull request or open an issue.
