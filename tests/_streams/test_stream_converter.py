# pylint: disable=protected-access
from unittest import TestCase

from parameterized import parameterized

from pystreamapi.__stream_converter import StreamConverter
from pystreamapi._streams.__parallel_stream import ParallelStream
from pystreamapi._streams.__sequential_stream import SequentialStream
from pystreamapi._streams.numeric.__parallel_numeric_stream import ParallelNumericStream
from pystreamapi._streams.numeric.__sequential_numeric_stream import SequentialNumericStream


class TestStreamConverter(TestCase):

    def test_convert_to_numeric_stream_sequential(self):
        stream = SequentialStream(["1", "2", "3"]).map_to_int()
        self.assertIsInstance(stream, SequentialNumericStream)

    def test_convert_to_numeric_stream_parallel(self):
        stream = ParallelStream(["1", "2", "3"]).map_to_int()
        self.assertIsInstance(stream, ParallelNumericStream)

    def test_convert_to_numeric_stream_numeric_parallel(self):
        stream = ParallelNumericStream(["1", "2", "3"]).map_to_int()
        self.assertIsInstance(stream, ParallelNumericStream)

    def test_convert_to_parallel_stream_sequential(self):
        stream = SequentialStream(["1", "2", "3"]).parallel()
        self.assertIsInstance(stream, ParallelStream)

    def test_convert_to_parallel_stream_sequential_numeric(self):
        stream = SequentialNumericStream(["1", "2", "3"]).parallel()
        self.assertIsInstance(stream, ParallelNumericStream)

    def test_convert_to_parallel_stream_parallel(self):
        stream = ParallelStream(["1", "2", "3"]).parallel()
        self.assertIsInstance(stream, ParallelStream)

    def test_convert_to_parallel_stream_parallel_numeric(self):
        stream = ParallelNumericStream(["1", "2", "3"]).parallel()
        self.assertIsInstance(stream, ParallelNumericStream)

    def test_convert_to_sequential_stream_sequential(self):
        stream = SequentialStream(["1", "2", "3"]).sequential()
        self.assertIsInstance(stream, SequentialStream)

    def test_convert_to_sequential_stream_sequential_numeric(self):
        stream = SequentialNumericStream(["1", "2", "3"]).sequential()
        self.assertIsInstance(stream, SequentialNumericStream)

    def test_convert_to_sequential_stream_parallel(self):
        stream = ParallelStream(["1", "2", "3"]).sequential()
        self.assertIsInstance(stream, SequentialStream)

    def test_convert_to_sequential_stream_parallel_numeric(self):
        stream = ParallelNumericStream(["1", "2", "3"]).sequential()
        self.assertIsInstance(stream, SequentialNumericStream)

    @parameterized.expand([("sequential stream", SequentialStream),
                           ("sequential numeric stream", SequentialNumericStream)])
    def test_convert_sequential_to_parallel_parallelizer_working(self, _, stream):
        res = []
        stream([1, 2, 3]).parallel().filter(lambda x: x > 1).for_each(res.append)
        self.assertEqual(res, [2, 3])

    def test_choose_implementation_with_parallelism_recommended(self):
        stream = SequentialStream([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        stream._is_parallelism_recommended = lambda: True

        result = StreamConverter.choose_implementation(stream)

        self.assertIsInstance(result, ParallelStream)

    def test_choose_implementation_with_parallelism_not_recommended(self):
        stream = SequentialStream([1, 2, 3])
        stream._is_parallelism_recommended = lambda: False

        result = StreamConverter.choose_implementation(stream)

        self.assertIsInstance(result, SequentialStream)
        self.assertIs(result, stream)

    def test_choose_implementation_with_explicit_implementation(self):
        stream = SequentialStream([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        stream._implementation_explicit = True
        stream._is_parallelism_recommended = lambda: True

        result = StreamConverter.choose_implementation(stream)

        self.assertIsInstance(result, SequentialStream)
        self.assertIs(result, stream)

    def test_choose_implementation_integration_with_operations(self):
        stream = SequentialStream(range(100))
        stream._is_parallelism_recommended = lambda: True

        result = StreamConverter.choose_implementation(stream)

        self.assertIsInstance(result, ParallelStream)

        filtered_result = result.filter(lambda x: x % 2 == 0).to_list()

        self.assertEqual(filtered_result, list(range(0, 100, 2)))

    def test_choose_implementation_with_numeric_stream(self):
        stream = SequentialNumericStream([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        stream._is_parallelism_recommended = lambda: True

        result = StreamConverter.choose_implementation(stream)

        self.assertIsInstance(result, ParallelNumericStream)

        sum_result = result.sum()
        self.assertEqual(sum_result, 55)
