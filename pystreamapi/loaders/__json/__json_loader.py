import json as jsonlib
from collections import namedtuple
from typing import Any, Iterator

from pystreamapi.loaders.__loader_utils import LoaderUtils


def json(src: str, read_from_src=False) -> Iterator[Any]:
    """
    Lazily loads JSON data from either a path or a string and yields namedtuples.

    Args:
        src (str): Either the path to a JSON file or a JSON string.
        read_from_src (bool): If True, src is treated as a JSON string.
        If False, src is treated as a path to a JSON file.

    Yields:
        namedtuple: Each object in the JSON as a namedtuple.
    """
    if read_from_src:
        return __lazy_load_json_string(src)
    path = LoaderUtils.validate_path(src)
    return __lazy_load_json_file(path)


def __lazy_load_json_file(file_path: str) -> Iterator[Any]:
    """Lazily read and parse a JSON file, yielding namedtuples."""

    def generator():
        # skipcq: PTC-W6004
        with open(file_path, mode='r', encoding='utf-8') as jsonfile:
            src = jsonfile.read()
            if src == '':
                return
            yield from jsonlib.loads(src, object_hook=__dict_to_namedtuple)

    return generator()


def __lazy_load_json_string(json_string: str) -> Iterator[Any]:
    """Lazily parse a JSON string, yielding namedtuples."""

    def generator():
        if not json_string.strip():
            return
        yield from jsonlib.loads(json_string, object_hook=__dict_to_namedtuple)

    return generator()


def __dict_to_namedtuple(d, name='Item'):
    """Convert a dictionary to a namedtuple"""
    if isinstance(d, dict):
        fields = list(d.keys())
        Item = namedtuple(name, fields)
        return Item(**{k: __dict_to_namedtuple(v, k) for k, v in d.items()})
    return d
