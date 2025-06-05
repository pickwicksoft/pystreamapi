import itertools
import unittest

from parameterized import parameterized_class

from pystreamapi.__optional import Optional
from pystreamapi._streams.__base_stream import BaseStream
from pystreamapi._streams.__parallel_stream import ParallelStream
from pystreamapi._streams.__sequential_stream import SequentialStream
from pystreamapi._streams.numeric.__numeric_base_stream import NumericBaseStream
from pystreamapi._streams.numeric.__parallel_numeric_stream import ParallelNumericStream
from pystreamapi._streams.numeric.__sequential_numeric_stream import SequentialNumericStream


def throwing_generator():
    i = 0
    while True:
        yield i
        i += 1
        if i > 1000:
            raise RecursionError("Infinite generator consumed wrong")


def finite_generator():
    yield from range(200)

@parameterized_class("stream", [
    [SequentialStream],
    [ParallelStream],
    [SequentialNumericStream],
    [ParallelNumericStream]])
class TestStreamImplementation(unittest.TestCase):

    def test_for_each(self):
        out = []
        self.stream([1, 2, 3, 9]).map_to_str().for_each(out.append)
        self.assertListEqual(out, ["1", "2", "3", "9"])

    def test_map_str_to_int(self):
        result = self.stream(["1", "2", "3", "9"]).map(int).to_list()
        self.assertListEqual(result, [1, 2, 3, 9])

    def test_map_str_to_int_then_str(self):
        result = self.stream(["1", "2", "3", "9"]).map(int).map(str).to_list()
        self.assertListEqual(result, ["1", "2", "3", "9"])

    def test_map_to_int(self):
        result = self.stream(["1", "2", "3", "9"]).map_to_int().to_list()
        self.assertListEqual(result, [1, 2, 3, 9])

    def test_map_to_int_empty(self):
        result = self.stream([]).map_to_int().to_list()
        self.assertListEqual(result, [])

    def test_map_to_int_returns_numeric_stream(self):
        result = self.stream(["1", "2", "3", "9"]).map_to_int()
        self.assertIsInstance(result, NumericBaseStream)

    def test_map_to_float(self):
        result = self.stream(["1", "2", "3", "9"]).map_to_float().to_list()
        self.assertListEqual(result, [1.0, 2.0, 3.0, 9.0])

    def test_map_to_float_empty(self):
        result = self.stream([]).map_to_float().to_list()
        self.assertListEqual(result, [])

    def test_map_to_float_returns_numeric_stream(self):
        result = self.stream(["1", "2", "3", "9"]).map_to_float()
        self.assertIsInstance(result, NumericBaseStream)

    def test_map_to_str(self):
        result = self.stream([1, 2, 3, 9]).map_to_str().to_list()
        self.assertListEqual(result, ["1", "2", "3", "9"])

    def test_convert_to_numeric_stream(self):
        result = self.stream([1, 2, 3, 9]).numeric()
        self.assertIsInstance(result, NumericBaseStream)

    def test_convert_to_numeric_stream_is_already_numeric(self):
        result = self.stream([1.0, 2.0, 3.0, 9.0]).numeric()
        self.assertIsInstance(result, NumericBaseStream)

    def test_flat_map(self):
        result = (self.stream([1, 2, 3, 9])
                  .flat_map(lambda x: self.stream([x, x])).to_list())
        self.assertListEqual(result, [1, 1, 2, 2, 3, 3, 9, 9])

    def test_flat_map_infinite_generator(self):
        # Parallel streams do not support generators
        result = (self.stream(throwing_generator()).sequential()
                  .flat_map(lambda x: self.stream([x, x * 2])).limit(6).to_list())
        self.assertListEqual(result, [0, 0, 1, 2, 2, 4])

    def test_flat_map_finite_generator(self):
        result = (self.stream(finite_generator())
                  .flat_map(lambda x: self.stream([x, x*2])).limit(6).to_list())
        self.assertListEqual(result, [0, 0, 1, 2, 2, 4])

    def test_filter_not_none(self):
        result = self.stream([1, 2, "3", None]).filter(lambda x: x is not None).to_list()
        self.assertListEqual(result, [1, 2, "3"])

    def test_filter_str(self):
        result = self.stream([1, 2, "3", None]).filter(lambda x: isinstance(x, str)).to_list()
        self.assertListEqual(result, ["3"])

    def test_filter_complex(self):
        result = self.stream([" ", '3', None, "2", 1, ""]) \
            .filter(lambda x: x is not None) \
            .map(str) \
            .map(lambda x: x.strip()) \
            .filter(lambda x: len(x) > 0) \
            .map(int) \
            .sorted() \
            .to_list()
        self.assertListEqual(result, [1, 2, 3])

    def test_filter_lazy(self):
        result = self.stream([1, 2, 3]).filter(lambda x: x > 1)
        self.assertListEqual(result.to_list(), [2, 3])
        self.assertIsInstance(result, BaseStream)

    def test_peek(self):
        src = []
        result = self.stream(["1", "2", "3", "9"]).map(int).peek(src.append).map(str).to_list()
        self.assertListEqual(result, ["1", "2", "3", "9"])
        self.assertListEqual(src, [1, 2, 3, 9])

    def test_all_match(self):
        result = self.stream([1, 2, 3, 9]).all_match(lambda x: x > 0)
        self.assertTrue(result)
        result = self.stream([1, 2, 3, 9]).all_match(lambda x: x > 1)
        self.assertFalse(result)
        result = self.stream([1, 2, 3, 9]).map_to_str().all_match(lambda x: isinstance(x, str))
        self.assertTrue(result)

    def test_all_match_empty(self):
        result = self.stream([]).all_match(lambda x: x > 0)
        self.assertTrue(result)

    def test_find_any(self):
        result = self.stream([1, 2, 3, 9]).find_any()
        self.assertEqual(result, Optional.of(1))

    def test_find_any_empty(self):
        result = self.stream([]).find_any()
        self.assertEqual(result, Optional.empty())

    def test_find_any_infinite_generator(self):
        result = self.stream(itertools.count()).find_any()
        self.assertEqual(result, Optional.of(0))

    def test_limit(self):
        result = self.stream([1, 2, 3, 9]).limit(2).to_list()
        self.assertListEqual(result, [1, 2])

    def test_limit_empty(self):
        result = self.stream([]).limit(2).to_list()
        self.assertListEqual(result, [])

    def test_reduce_no_identity(self):
        src = [1, 2, 3, 4, 5]
        result = self.stream(src).reduce(lambda x, y: x + y)
        self.assertEqual(result.or_else("Empty"), sum(src))

    def test_reduce_with_identity(self):
        src = [1, 2, 3, 4, 5]
        result = self.stream(src).reduce(lambda x, y: x + y, identity=0)
        self.assertEqual(type(result), int)
        self.assertEqual(result, sum(src))

    def test_reduce_depends_on_state(self):
        src = [4, 3, 2, 1]
        result = self.stream(src).reduce(lambda x, y: x - y, depends_on_state=True)
        self.assertEqual(result.get(), -2)

    def test_reduce_empty_stream_no_identity(self):
        result = self.stream([]).reduce(lambda x, y: x + y)
        self.assertEqual(result, Optional.empty())

    def test_reduce_empty_stream_with_identity(self):
        result = self.stream([]).reduce(lambda x, y: x + y, identity=0)
        self.assertEqual(result, 0)

    def test_group_by(self):
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        pt1, pt2, pt3, pt4 = Point(1, 2), Point(1, 3), Point(2, 3), Point(2, 4)
        result = self.stream([pt1, pt2, pt3, pt4]) \
            .group_by(lambda p: p.x) \
            .to_list()
        self.assertListEqual(result, [(1, [pt1, pt2]), (2, [pt3, pt4])])

    def test_group_by_empty(self):
        result = self.stream([]).group_by(lambda x: x).to_list()
        self.assertListEqual(result, [])

    def test_to_dict(self):
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        pt1, pt2, pt3, pt4 = Point(1, 2), Point(1, 3), Point(2, 3), Point(2, 4)
        result = self.stream([pt1, pt2, pt3, pt4]) \
            .to_dict(lambda p: p.x)
        self.assertDictEqual(result, {1: [pt1, pt2], 2: [pt3, pt4]})

    def test_to_dict_empty(self):
        result = self.stream([]).to_dict(lambda x: x)
        self.assertDictEqual(result, {})

    def test_handling_of_infinite_generator(self):
        # Parallel streams do not support generators
        result = (self.stream(throwing_generator()).sequential()
                  .map(lambda x: x * 2).filter(lambda x: x < 10).limit(5).to_list())
        self.assertListEqual(result, [0, 2, 4, 6, 8])

    def test_handling_of_finite_generator(self):
        result = (self.stream(finite_generator()).sequential()
                  .map(lambda x: x * 2).filter(lambda x: x < 10).limit(5).to_list())
        self.assertListEqual(result, [0, 2, 4, 6, 8])


if __name__ == '__main__':
    unittest.main()
