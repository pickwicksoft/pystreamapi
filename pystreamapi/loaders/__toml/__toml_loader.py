import tomlkit
from collections import namedtuple
from typing import Any, Iterator

from pystreamapi.loaders.__loader_utils import LoaderUtils


def toml(src: str, read_from_src=False) -> Iterator[Any]:
    """
    Lazily loads TOML data from either a path or a string and yields namedtuples.

    Args:
        src (str): Either the path to a TOML file or a TOML string.
        read_from_src (bool): If True, src is treated as a TOML string.
        If False, src is treated as a path to a TOML file.

    Yields:
        namedtuple: The TOML document as a namedtuple.
    """
    if read_from_src:
        return __lazy_load_toml_string(src)
    path = LoaderUtils.validate_path(src)
    return __lazy_load_toml_file(path)


def __lazy_load_toml_file(file_path: str) -> Iterator[Any]:
    """Lazily read and parse a TOML file, yielding a namedtuple."""

    def generator():
        """Generate a namedtuple from the TOML file contents."""
        # skipcq: PTC-W6004
        with open(file_path, mode='r', encoding='utf-8') as tomlfile:
            src = tomlfile.read()
            if not src.strip():
                return
            result = tomlkit.loads(src)
            yield __dict_to_namedtuple(result)

    return generator()


def __lazy_load_toml_string(toml_string: str) -> Iterator[Any]:
    """Lazily parse a TOML string, yielding a namedtuple."""

    def generator():
        """Internal generator that yields a namedtuple by parsing the TOML string on demand."""
        if not toml_string.strip():
            return
        result = tomlkit.loads(toml_string)
        yield __dict_to_namedtuple(result)

    return generator()


def __dict_to_namedtuple(d, name='Item'):
    """Recursively convert a dictionary (or list) to namedtuples."""
    if isinstance(d, dict):
        fields = list(d.keys())
        Item = namedtuple(name, fields)
        return Item(**{k: __dict_to_namedtuple(v, k) for k, v in d.items()})
    if isinstance(d, list):
        return [__dict_to_namedtuple(item, name) for item in d]
    return d
