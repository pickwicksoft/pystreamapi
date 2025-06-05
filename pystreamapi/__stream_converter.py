# pylint: disable=protected-access
from pystreamapi._streams.__base_stream import BaseStream
from pystreamapi._streams.__parallel_stream import ParallelStream
from pystreamapi._streams.__sequential_stream import SequentialStream
from pystreamapi._streams.numeric.__numeric_base_stream import NumericBaseStream
from pystreamapi._streams.numeric.__parallel_numeric_stream import ParallelNumericStream
from pystreamapi._streams.numeric.__sequential_numeric_stream import SequentialNumericStream


class StreamConverter:
    """Class for converting streams to other types of streams."""

    @staticmethod
    def to_numeric_stream(stream: BaseStream) -> NumericBaseStream:
        """Converts a stream to a numeric stream."""
        if isinstance(stream, SequentialStream):
            stream.__class__ = SequentialNumericStream
        if isinstance(stream, ParallelStream):
            stream.__class__ = ParallelNumericStream
            stream._init_parallelizer()
        return stream

    @staticmethod
    def to_parallel_stream(stream: BaseStream) -> ParallelStream:
        """Converts a stream to a parallel stream."""
        if isinstance(stream, SequentialNumericStream):
            stream.__class__ = ParallelNumericStream
            stream._init_parallelizer()
        elif isinstance(stream, SequentialStream):
            stream.__class__ = ParallelStream
            stream._init_parallelizer()
        stream._set_implementation_explicit()
        return stream

    @staticmethod
    def to_sequential_stream(stream: BaseStream) -> SequentialStream:
        """Converts a stream to a sequential stream."""
        if isinstance(stream, ParallelNumericStream):
            stream.__class__ = SequentialNumericStream
        elif isinstance(stream, ParallelStream):
            stream.__class__ = SequentialStream
        stream._set_implementation_explicit()
        return stream

    @staticmethod
    def choose_implementation(stream: BaseStream) -> BaseStream:
        """
        Chooses the implementation of the stream based on whether
        parallelization is recommended or not.
        """
        if not stream._implementation_explicit and stream._is_parallelism_recommended():
                return StreamConverter.to_parallel_stream(stream)
        return stream
