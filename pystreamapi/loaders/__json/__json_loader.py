import io
from collections import namedtuple
from typing import Any, Iterator

try:
    import ijson
except ImportError as exc:
    raise ImportError(
        "Please install the json_loader extra dependency (ijson) to use the json loader."
    ) from exc

from pystreamapi.loaders.__loader_utils import LoaderUtils

_PEEK_SIZE = 4096


class _TextToBytesWrapper:
    """Wraps a text-mode file handle and converts its output to bytes for ijson."""

    def __init__(self, handle, encoding='utf-8'):
        self._handle = handle
        self._encoding = encoding

    def read(self, size=-1):
        data = self._handle.read(size)
        if isinstance(data, str):
            return data.encode(self._encoding)
        return data if data else b''


class _PeekableBytesReader:
    """Replays a pre-read buffer before delegating further reads to the underlying source."""

    def __init__(self, buffer: bytes, source):
        self._buf = buffer
        self._src = source

    def read(self, size=-1):
        if size == -1:
            tail = self._src.read()
            if isinstance(tail, str):
                tail = tail.encode('utf-8')
            result = self._buf + tail
            self._buf = b''
            return result
        if len(self._buf) >= size:
            result = self._buf[:size]
            self._buf = self._buf[size:]
            return result
        needed = size - len(self._buf)
        more = self._src.read(needed)
        if isinstance(more, str):
            more = more.encode('utf-8')
        result = self._buf + more
        self._buf = b''
        return result


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
    """Lazily read and parse a JSON file, yielding namedtuples incrementally."""

    def generator():
        """Yield namedtuples from the JSON file using a streaming parser."""
        # skipcq: PTC-W6004
        with open(file_path, mode='r', encoding='utf-8') as jsonfile:
            yield from __stream_json_items(jsonfile)

    return generator()


def __lazy_load_json_string(json_string: str) -> Iterator[Any]:
    """Lazily parse a JSON string, yielding namedtuples incrementally."""

    def generator():
        """Yield namedtuples by streaming-parsing the JSON string."""
        yield from __stream_json_items(io.StringIO(json_string))

    return generator()


def __stream_json_items(handle) -> Iterator[Any]:
    """Stream JSON items from a text-mode file-like handle using ijson.

    Reads an initial chunk to detect whether the root value is an array or a
    single object, then replays that chunk together with the remainder of the
    handle through a bytes wrapper so that ijson can parse incrementally.
    """
    initial = handle.read(_PEEK_SIZE)
    if isinstance(initial, str):
        initial_str = initial
        initial_bytes = initial.encode('utf-8')
    else:
        initial_bytes = initial
        initial_str = initial.decode('utf-8', errors='replace')

    stripped = initial_str.lstrip()
    if not stripped:
        return

    first_char = stripped[0]
    reader = _PeekableBytesReader(initial_bytes, _TextToBytesWrapper(handle))

    if first_char == '[':
        for item in ijson.items(reader, 'item', use_float=True):
            yield __dict_to_namedtuple(item)
    else:
        obj = next(ijson.items(reader, '', use_float=True), None)
        if obj is not None:
            yield __dict_to_namedtuple(obj)


def __dict_to_namedtuple(d, name='Item'):
    """Convert a dictionary (and any nested dicts/lists) to namedtuples recursively."""
    if isinstance(d, dict):
        fields = list(d.keys())
        Item = namedtuple(name, fields)
        return Item(**{k: __dict_to_namedtuple(v, k) for k, v in d.items()})
    if isinstance(d, list):
        return [__dict_to_namedtuple(item) for item in d]
    return d
