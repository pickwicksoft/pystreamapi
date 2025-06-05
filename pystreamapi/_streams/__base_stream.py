# pylint: disable=protected-access
from __future__ import annotations

import functools
import itertools
from abc import abstractmethod
from builtins import reversed
from collections.abc import Sized
from functools import cmp_to_key
from typing import Iterable, Callable, Any, TypeVar, Iterator, TYPE_CHECKING, Union

from pystreamapi.__optional import Optional
from pystreamapi._itertools.tools import dropwhile, distinct, limit
from pystreamapi._lazy.process import Process
from pystreamapi._lazy.queue import ProcessQueue
from pystreamapi._streams.error.__error import ErrorHandler
from pystreamapi._streams.error.__levels import ErrorLevel

if TYPE_CHECKING:
    from pystreamapi._streams.numeric.__numeric_base_stream import NumericBaseStream
    from pystreamapi._streams.__parallel_stream import ParallelStream
    from pystreamapi._streams.__sequential_stream import SequentialStream

K = TypeVar('K')
_V = TypeVar('_V')
_identity_missing = object()


def _operation(func):
    """
    Decorator to execute all the processes in the queue before executing the decorated function.
    To be applied to intermediate operations.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> BaseStream[K]:
        self: BaseStream = args[0]
        self._verify_open()
        return func(*args, **kwargs)

    return wrapper


def terminal(func):
    """
    Decorator to execute all the processes in the queue before executing the decorated function.
    To be applied to terminal operations.
    """
    @functools.wraps(func)
    @_operation
    def wrapper(*args, **kwargs) -> BaseStream[K]:
        # pylint: disable=import-outside-toplevel
        from pystreamapi.__stream_converter import StreamConverter
        self: BaseStream = args[0]
        self._verify_open()
        self = StreamConverter.choose_implementation(self)
        self._queue.execute_all()
        self._close()
        return func(*args, **kwargs)

    return wrapper


class BaseStream(Iterable[K], ErrorHandler):
    """
    A sequence of elements supporting sequential and parallel aggregate operations.

    To perform a computation, stream operations are composed into a stream pipeline. A stream
    pipeline consists of a source (which might be an iterable, a collection, a generator function,
    an I/O channel, etc.), zero or more intermediate operations (which transform a stream into
    another stream, such as filter(Predicate)), and a terminal operation (which produces a result
    or side effect, such as count() or forEach(Consumer)). Streams are lazy; computation on the
    source data is only performed when the terminal operation is initiated, and source elements
    are consumed only as needed.
    """

    def __init__(self, source: Iterable[K]):
        self._source = source
        self._queue = ProcessQueue()
        self._open = True
        self._implementation_explicit = False
        self.__PARALLELISM_RECOMMENDATION_THRESHOLD = 3000

    def _close(self):
        """Close the stream."""
        self._open = False

    def _verify_open(self):
        """Verify if stream is open. If not, raise an exception."""
        if not self._open:
            raise RuntimeError("The stream has been closed")

    def _is_parallelism_recommended(self) -> bool:
        """Determines if parallelism is recommended for the current stream."""
        if isinstance(self._source, Sized):
            for item in self._queue.get_queue():
                if (item.has_name(self._filter)
                        and len(self._source) > self.__PARALLELISM_RECOMMENDATION_THRESHOLD):
                    return True
        return False

    def _set_implementation_explicit(self):
        """
        Sets the implementation as explicit, meaning that the stream will not be converted to a
        different implementation (e.g., from sequential to parallel) automatically.
        """
        self._implementation_explicit = True

    @terminal
    def __iter__(self) -> Iterator[K]:
        return iter(self._source)

    def concat(self, *streams: "BaseStream[K]") -> BaseStream[K]:
        """
        Creates a lazily concatenated stream whose elements are all the elements of the first stream
        followed by all the elements of the other streams.

        :param streams: The streams to concatenate
        :return: The concatenated stream
        """
        self._queue.execute_all()
        for stream in streams:
            stream._queue.execute_all()
        self._source = itertools.chain(self._source, *[stream._source for stream in streams])
        return self

    @_operation
    def distinct(self) -> 'BaseStream[K]':
        """Returns a stream consisting of the distinct elements of this stream."""
        self._queue.append(Process(self.__distinct))
        return self

    def __distinct(self):
        """Removes duplicate elements from the stream."""
        self._source = distinct(self._source)

    @_operation
    def drop_while(self, predicate: Callable[[K], bool]) -> 'BaseStream[K]':
        """
        Returns, if this stream is ordered, a stream consisting of the remaining elements of this
        stream after dropping the longest prefix of elements that match the given predicate.

        :param predicate:
        """
        self._queue.append(Process(self.__drop_while, predicate))
        return self

    def __drop_while(self, predicate: Callable[[Any], bool]):
        """Drops elements from the stream while the predicate is true."""
        self._source = dropwhile(predicate, self._source, self)

    def error_level(self, level: ErrorLevel, *exceptions)\
            -> Union["BaseStream[K]", NumericBaseStream]:
        """
        Sets the error level of the stream. If an exception is raised during the execution of the
        stream, the error level determines what to do with the exception.
        :param level: Error level from ErrorLevel
        :param exceptions: Exceptions to ignore. If not provided, all exceptions will be ignored
        :return: The stream itself
        """
        self._queue.append(Process(lambda: self._error_level(level, *exceptions)))
        return self

    @_operation
    def filter(self, predicate: Callable[[K], bool]) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the elements of this stream that match the given predicate.

        :param predicate:
        """
        self._queue.append(Process(self._filter, predicate))
        return self

    @abstractmethod
    def _filter(self, predicate: Callable[[K], bool]):
        """Implementation of filter. Should be implemented by subclasses."""

    @_operation
    def flat_map(self, predicate: Callable[[K], Iterable[_V]]) -> 'BaseStream[_V]':
        """
        Returns a stream consisting of the results of replacing each element of this stream with
        the contents of a mapped stream produced by applying the provided mapping function to
        each element.

        :param predicate:
        """
        self._queue.append(Process(self._flat_map, predicate))
        return self

    @abstractmethod
    def _flat_map(self, mapper: Callable[[K], Iterable[_V]]):
        """Implementation of flat_map. Should be implemented by subclasses."""

    @_operation
    def group_by(self, key_mapper: Callable[[K], Any]) -> 'BaseStream[K]':
        """
        Returns a Stream consisting of the results of grouping the elements of this stream
        by the given classifier and extracting the key/value pairs.

        :param key_mapper:
        """
        self._queue.append(Process(self.__group_by, key_mapper))
        return self

    def __group_by(self, key_mapper: Callable[[Any], Any]):
        """Groups the stream by the given key mapper. Uses the implementation of _group_to_dict."""
        groups = self._group_to_dict(key_mapper)
        self._source = groups.items()

    @abstractmethod
    def _group_to_dict(self, key_mapper: Callable[[K], Any]) -> dict[K, list]:
        """Groups the stream into a dictionary. Should be implemented by subclasses."""

    @_operation
    def limit(self, max_size: int) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the elements of this stream, truncated to be no longer
        than maxSize in length.

        :param max_size:
        """
        self._queue.append(Process(self.__limit, max_size))
        return self

    def __limit(self, max_size: int):
        """Limits the stream to the first n elements."""
        self._source = limit(self._source, max_size)

    @_operation
    def map(self, mapper: Callable[[K], _V]) -> 'BaseStream[_V]':
        """
        Returns a stream consisting of the results of applying the given function to the elements
        of this stream.

        :param mapper:
        """
        self._queue.append(Process(self._map, mapper))
        return self

    @abstractmethod
    def _map(self, mapper: Callable[[K], _V]):
        """Implementation of map. Should be implemented by subclasses."""

    @_operation
    def map_to_int(self) -> NumericBaseStream:
        """
        Returns a stream consisting of the results of converting the elements of this stream to
        integers.
        """
        self._queue.append(Process(self.__map_to_int))
        return self._to_numeric_stream()

    def __map_to_int(self):
        """Converts the stream to integers."""
        self._map(int)

    def map_to_float(self) -> NumericBaseStream:
        """
        Returns a stream consisting of the results of converting the elements of this stream to
        floats.
        """
        self._queue.append(Process(self.__map_to_float))
        return self._to_numeric_stream()

    def __map_to_float(self):
        """Converts the stream to floats."""
        self._map(float)

    @_operation
    def map_to_str(self) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the results of converting the elements of this stream to
        strings.
        """
        self._queue.append(Process(self.__map_to_str))
        return self

    def __map_to_str(self):
        """Converts the stream to strings."""
        self._map(str)

    def numeric(self) -> NumericBaseStream:
        """Returns a numeric stream. If the stream is already numeric, it is returned."""
        return self._to_numeric_stream()

    @_operation
    def parallel(self) -> 'ParallelStream[K]':
        """Returns a parallel stream. If the stream is already parallel, it is returned."""
        # pylint: disable=import-outside-toplevel
        from pystreamapi.__stream_converter import StreamConverter
        return StreamConverter.to_parallel_stream(self)

    @_operation
    def peek(self, action: Callable) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the elements of this stream, additionally performing the
        provided action on each element as elements are consumed from the resulting stream.

        :param action:
        """
        self._queue.append(Process(self._peek, action))
        return self

    @abstractmethod
    @_operation
    def _peek(self, action: Callable):
        """Implementation of peek. Should be implemented by subclasses."""

    @_operation
    def reversed(self) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the elements of this stream, with their order being
        reversed.
        This does not work on infinite generators.
        """
        self._queue.append(Process(self.__reversed))
        return self

    def __reversed(self):
        """Reverses the stream."""
        try:
            self._source = reversed(self._source)
        except TypeError:
            self._source = reversed(list(self._source))

    @_operation
    def sequential(self) -> SequentialStream[K]:
        """Returns a sequential stream. If the stream is already sequential, it is returned."""
        # pylint: disable=import-outside-toplevel
        from pystreamapi.__stream_converter import StreamConverter
        return StreamConverter.to_sequential_stream(self)

    @_operation
    def skip(self, n: int) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the remaining elements of this stream after discarding the
        first n elements of the stream.

        :param n:
        """
        self._queue.append(Process(self.__skip, n))
        return self

    def __skip(self, n: int):
        """Skips the first n elements of the stream."""
        self._source = itertools.islice(self._source, n, None)

    @_operation
    def sorted(self, comparator: Callable[[K], int] = None) -> 'BaseStream[K]':
        """
        Returns a stream consisting of the elements of this stream, sorted according to natural
        order.
        """
        self._queue.append(Process(self.__sorted, comparator))
        return self

    def __sorted(self, comparator: Callable[[K], int] = None):
        """Sorts the stream."""
        if comparator is None:
            self._source = sorted(self._source)
        else:
            self._source = sorted(self._source, key=cmp_to_key(comparator))

    @_operation
    def take_while(self, predicate: Callable[[K], bool]) -> 'BaseStream[K]':
        """
        Returns, if this stream is ordered, a stream consisting of the longest prefix of elements
        taken from this stream that match the given predicate.

        :param predicate:
        """
        self._queue.append(Process(self.__take_while, predicate))
        return self

    def __take_while(self, predicate: Callable[[Any], bool]):
        """Takes elements from the stream while the predicate is true."""
        self._source = itertools.takewhile(predicate, self._source)

    @abstractmethod
    @terminal
    def all_match(self, predicate: Callable[[K], bool]):
        """
        Returns whether all elements of this stream match the provided predicate.

        :param predicate: The callable predicate
        """

    @terminal
    def any_match(self, predicate: Callable[[K], bool]):
        """
        Returns whether any elements of this stream match the provided predicate.

        :param predicate: The callable predicate
        """
        def _one_wrapper(iterable, mapper):
            """Generator wrapper for any_match."""
            for i in iterable:
                yield self._one(mapper, item=i)

        self._source = _one_wrapper(self._source, predicate)
        return any(self._source)

    @terminal
    def count(self):
        """
        Returns the count of elements in this stream.

        :return: Number of elements in the stream
        """
        return len(self._source)

    @abstractmethod
    @terminal
    def find_any(self) -> Optional:
        """
        Returns an Optional describing some element of the stream, or an empty Optional if the
        stream is empty.
        """

    @terminal
    def find_first(self):
        """
        Returns an Optional describing the first element of this stream, or an empty Optional if
        the stream is empty. :return:
        """
        if len(self._source) > 0:
            return Optional.of(self._source[0])
        return Optional.empty()

    @abstractmethod
    @terminal
    def for_each(self, action: Callable):
        """
        Performs an action for each element of this stream.

        :param action:
        """

    @terminal
    def none_match(self, predicate: Callable[[K], bool]):
        """
        Returns whether no elements of this stream match the provided predicate.

        :param predicate:
        """
        return not any(self._itr(self._source, predicate))

    @terminal
    def min(self):
        """Returns the minimum element of this stream."""
        self._source = list(self._source)
        if len(self._source) > 0:
            return Optional.of(min(self._source))
        return Optional.empty()

    @terminal
    def max(self):
        """Returns the maximum element of this stream."""
        self._source = list(self._source)
        if len(self._source) > 0:
            return Optional.of(max(self._source))
        return Optional.empty()

    @abstractmethod
    @terminal
    def reduce(self, predicate: Callable[[K, K], K], identity=_identity_missing,
               depends_on_state=False) -> Optional:
        """
        Performs a reduction on the elements of this stream, using the provided identity value
        and an associative accumulation function, and returns the reduced value.

        :param depends_on_state: Weather processing order changes result or not
        :param predicate:
        :param identity: Default value
        """

    @terminal
    def to_list(self):
        """Accumulates the elements of this stream into a List."""
        return list(self._source)

    @terminal
    def to_tuple(self):
        """Accumulates the elements of this stream into a Tuple."""
        return tuple(self._source)

    @terminal
    def to_set(self):
        """Accumulates the elements of this stream into a Set."""
        return set(self._source)

    @abstractmethod
    @terminal
    def to_dict(self, key_mapper: Callable[[K], Any]) -> dict:
        """
        Returns a dictionary consisting of the results of grouping the elements of this stream
        by the given classifier.

        :param key_mapper:
        """

    def _to_numeric_stream(self) -> NumericBaseStream:
        """Converts a stream to a numeric stream using the stream converter"""
        # pylint: disable=import-outside-toplevel
        from pystreamapi.__stream_converter import StreamConverter
        return StreamConverter.to_numeric_stream(self)
