from collections import defaultdict
from typing import Callable, Any

import pystreamapi._streams.__base_stream as stream
from pystreamapi.__optional import Optional
from pystreamapi._itertools.tools import reduce, flat_map, peek
from pystreamapi._streams.__base_stream import terminal
from pystreamapi._streams.error.__error import _sentinel

_identity_missing = object()


class SequentialStream(stream.BaseStream):
    """The sequential implementation of BaseStream"""

    @terminal
    def all_match(self, predicate: Callable[[Any], bool]):
        return all(self._itr(self._source, mapper=predicate))

    def _filter(self, predicate: Callable[[Any], bool]):
        self._source = self._itr(self._source, condition=predicate)

    @terminal
    def find_any(self):
        try:
            return Optional.of(next(iter(self._source)))
        except StopIteration:
            return Optional.empty()

    def _flat_map(self, mapper: Callable[[Any], stream.BaseStream]):
        self._source = flat_map(self._itr(self._source, mapper=mapper))

    def _group_to_dict(self, key_mapper: Callable[[Any], Any]):
        groups = defaultdict(list)

        for element in self._source:
            key = self._one(mapper=key_mapper, item=element)
            if key == _sentinel:
                continue
            groups[key].append(element)
        return groups

    @terminal
    def for_each(self, action: Callable):
        for item in self._source:
            self._one(mapper=action, item=item)

    def _map(self, mapper: Callable[[Any], Any]):
        self._source = self._itr(self._source, mapper=mapper)

    def _peek(self, action: Callable):
        self._source = peek(self._source, lambda x: self._one(mapper=action, item=x))

    @terminal
    def reduce(self, predicate: Callable, identity=_identity_missing, depends_on_state=False):
        if len(self._source) > 0:
            if identity is not _identity_missing:
                return reduce(predicate, self._source)
            return Optional.of(reduce(predicate, self._source, handler=self))
        return identity if identity is not _identity_missing else Optional.empty()

    @terminal
    def to_dict(self, key_mapper: Callable[[Any], Any]) -> dict:
        return self._group_to_dict(key_mapper)
