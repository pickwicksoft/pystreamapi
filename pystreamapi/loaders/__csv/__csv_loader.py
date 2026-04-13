from collections import namedtuple
from csv import reader
from io import StringIO
from typing import Any, Iterator

from pystreamapi.loaders.__loader_utils import LoaderUtils


def csv(
        src: str, read_from_src=False, cast_types=True, delimiter=',', encoding="utf-8"
) -> Iterator[Any]:
    """
    Lazily loads CSV data from either a path or a string and yields namedtuples.

    Args:
        src (str): Either the path to a CSV file or a CSV string.
        read_from_src (bool): If True, src is treated as a CSV string.
        If False, src is treated as a path to a CSV file.
        cast_types (bool): Set as False to disable casting of values to int, bool or float.
        delimiter (str): The delimiter used in the CSV data.
        encoding (str): The encoding of the CSV file (only used when reading from file).

    Yields:
        namedtuple: Each row in the CSV as a namedtuple.
    """
    if not read_from_src:
        src = LoaderUtils.validate_path(src)
        return __load_csv_from_file(src, cast_types, delimiter, encoding)
    return __load_csv_from_string(src, cast_types, delimiter)


def __load_csv_from_file(file_path, cast, delimiter, encoding):
    """Load a CSV file and convert it into a generator of namedtuples"""
    # skipcq: PTC-W6004
    with open(file_path, mode='r', newline='', encoding=encoding) as csvfile:
        yield from __process_csv(csvfile, cast, delimiter)


def __load_csv_from_string(csv_string, cast, delimiter):
    """Load a CSV from string and convert it into a generator of namedtuples"""
    with StringIO(csv_string) as csvfile:
        yield from __process_csv(csvfile, cast, delimiter)


def __process_csv(csvfile, cast, delimiter):
    """Process CSV data and yield namedtuples"""
    csvreader = reader(csvfile, delimiter=delimiter)

    # Create a namedtuple type, casting the header values to int or float if possible
    header = __get_csv_header(csvreader)
    if not header:
        return

    Row = namedtuple('Row', list(header))
    mapper = LoaderUtils.try_cast if cast else lambda x: x

    # Yield the data row by row, casting values to int or float if possible
    for row in csvreader:
        yield Row(*[mapper(value) for value in row])


def __get_csv_header(csvreader):
    """Get the header of a CSV file. If the header is empty, return an empty list"""
    while True:
        try:
            header = next(csvreader)
            if header:
                break
        except StopIteration:
            return []
    return header
