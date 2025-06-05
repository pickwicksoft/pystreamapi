import itertools
from collections.abc import Sized
from typing import Iterable, TypeVar, Callable, Optional, overload, Union, Generator

from pystreamapi.__iterate import iterate
from pystreamapi._streams.__base_stream import BaseStream
from pystreamapi._streams.__parallel_stream import ParallelStream
from pystreamapi._streams.__sequential_stream import SequentialStream
from pystreamapi._streams.numeric.__numeric_base_stream import NumericBaseStream
from pystreamapi._streams.numeric.__sequential_numeric_stream import SequentialNumericStream

_K = TypeVar('_K')


class Stream:
    """The stream builder"""

    @staticmethod
    @overload
    def of(source: Iterable[Union[int, float]]) -> NumericBaseStream:
        """
        Create a new Stream from a numerical source. The implementation will decide whether to use a
        sequential or a parallel stream

        :param source:
        """

    @staticmethod
    @overload
    def of(source: Iterable[_K]) -> BaseStream[_K]:
        """
        Create a new Stream from a source. The implementation will decide whether to use a
        sequential or a parallel stream

        :param source:
        """

    @staticmethod
    @overload
    def of(source: Generator[_K, None, None]) -> NumericBaseStream:
        """
        Create a new Stream from a generator. The implementation will use a sequential stream.
        If you need a parallel or numeric stream, use the appropriate method.

        :param source:
        """

    @staticmethod
    def of(source: Union[Iterable, Generator, Sized]):
        """
        Create a new Stream from a source. The implementation will decide whether to use a
        sequential or a parallel stream

        :param source:
        """
        # Check if the source is a numeric iterable (source can be a generator)
        if isinstance(source, Iterable) and isinstance(source, Sized) \
                and all(isinstance(x, (int, float)) for x in source):
            return SequentialNumericStream(source)
        return SequentialStream(source)

    @staticmethod
    def of_noneable(source: Optional[Iterable[_K]]) -> BaseStream[_K]:
        """
        Create a new Stream from a source. The implementation will decide whether to use a
        sequential or a parallel stream.

        If the source is None, an empty stream will be returned.

        :param source: The source to create the stream from. Can be None.
        """
        return Stream.of([]) if source is None else SequentialStream(source)

    @staticmethod
    def parallel_of(source: Iterable[_K]) -> BaseStream[_K]:
        """
        Create a parallel stream from a source

        :param source:
        """
        return ParallelStream(source)

    @staticmethod
    def sequential_of(source: Iterable[_K]) -> BaseStream[_K]:
        """
        Create a sequential stream from a source

        :param source:
        """
        return SequentialStream(source)

    @staticmethod
    def concat(*streams: "BaseStream[_K]"):
        """
        Creates a lazily concatenated stream whose elements are all the elements of the first stream
        followed by all the elements of the other streams.

        :param streams: The streams to concatenate
        :return: The concatenated stream
        """
        return streams[0].__class__(itertools.chain(*iter(streams)))

    @staticmethod
    def iterate(seed: _K, func: Callable[[_K], _K]) -> BaseStream[_K]:
        """
        Returns an infinite sequential ordered Stream produced by iterative application of a
        function f to an initial element seed, producing a Stream consisting of seed,
        f(seed), f(f(seed)), etc.

        :param seed: The initial element
        :param func: The function to apply
        """
        return Stream.of(
            iterate(func, seed))
