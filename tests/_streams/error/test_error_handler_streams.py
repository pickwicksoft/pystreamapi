import unittest

from parameterized import parameterized_class

from pystreamapi._streams.__parallel_stream import ParallelStream
from pystreamapi._streams.__sequential_stream import SequentialStream
from pystreamapi._streams.error.__levels import ErrorLevel
from pystreamapi._streams.numeric.__parallel_numeric_stream import ParallelNumericStream
from pystreamapi._streams.numeric.__sequential_numeric_stream import SequentialNumericStream


class NoToString:
    def __str__(self):
        raise ValueError("No to string")

@parameterized_class("stream", [
    [SequentialStream],
    [ParallelStream],
    [SequentialNumericStream],
    [ParallelNumericStream]])
class TestStreamImplementation(unittest.TestCase):

    def test_drop_while_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, 4, 5, "a", 6])\
                .drop_while(lambda x: int(x) < 6).to_list()

    def test_drop_while_ignore(self):
        result = self.stream([1, 2, 3, 4, "a", 5, 6, 7, 8])\
            .error_level(ErrorLevel.IGNORE) \
            .drop_while(lambda x: int(x) < 5).to_list()
        self.assertListEqual(result, [5, 6, 7, 8])

    def test_filter_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, 4, 5, "a", 6])\
                .filter(lambda x: int(x) < 6).to_list()

    def test_filter_ignore(self):
        result = self.stream([1, "a", "3"]).error_level(ErrorLevel.IGNORE)\
            .filter(lambda x: int(x) < 6).to_list()
        self.assertListEqual(result, [1, "3"])

    def test_flat_map_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a"]).error_level(ErrorLevel.RAISE) \
                .flat_map(lambda x: self.stream([int(x), int(x)])).to_list()

    def test_flat_map_ignore(self):
        result = self.stream([1, 2, 3, "a"]).error_level(ErrorLevel.IGNORE)\
            .flat_map(lambda x: self.stream([int(x), int(x)])).to_list()
        self.assertListEqual(result, [1, 1, 2, 2, 3, 3])

    def test_group_by_raise(self):
        with self.assertRaises(AttributeError):
            self.stream([1, "b", "a"])\
                .error_level(ErrorLevel.RAISE)\
                .group_by(lambda x: x.isalnum())\
                .to_list()

    def test_group_by_ignore(self):
        result = self.stream([1, "b", "a"])\
            .error_level(ErrorLevel.IGNORE)\
            .group_by(lambda x: x.isalnum())\
            .to_list()
        self.assertIn(result, [
            [(True, ['b', 'a'])],
            [(True, ['a', 'b'])]
        ])

    def test_map_str_to_int_raise(self):
        with self.assertRaises(ValueError):
            self.stream(["1", "2", "3", "a"]).error_level(ErrorLevel.RAISE) \
                .map(int).to_list()

    def test_map_str_to_int_ignore(self):
        result = self.stream(["1", "2", "3", "a"])\
            .error_level(ErrorLevel.IGNORE).map(int).to_list()
        self.assertListEqual(result, [1, 2, 3])

    def test_map_to_int_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a"])\
                .error_level(ErrorLevel.RAISE).map_to_int().to_list()

    def test_map_to_int_ignore(self):
        result = self.stream([1, 2, 3, "a"])\
            .error_level(ErrorLevel.IGNORE).map_to_int().to_list()
        self.assertListEqual(result, [1, 2, 3])

    def test_map_to_str_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, NoToString(), "a"])\
                .error_level(ErrorLevel.RAISE).map_to_str().to_list()

    def test_map_to_str_ignore(self):
        result = self.stream([1, 2, NoToString(), "a"])\
            .error_level(ErrorLevel.IGNORE).map_to_str().to_list()
        self.assertListEqual(result, ["1", "2", "a"])

    def test_peek_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a"]) \
                .error_level(ErrorLevel.RAISE).peek(int).to_list()

    def test_peek_ignore(self):
        result = self.stream([1, 2, 3, "a"])\
            .error_level(ErrorLevel.IGNORE).peek(int).to_list()
        self.assertListEqual(result, [1, 2, 3, "a"])

    def test_take_while_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a", 4])\
                .error_level(ErrorLevel.RAISE).take_while(lambda x: int(x) < 4).to_list()

    def test_take_while_ignore(self):
        result = self.stream([1, 2, 3, "a"])\
            .error_level(ErrorLevel.IGNORE).take_while(lambda x: int(x) < 3).to_list()
        self.assertListEqual(result, [1, 2])

    def test_all_match_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a"]).all_match(lambda x: int(x) > 0)

    def test_all_match_ignore(self):
        self.assertFalse(self.stream([1, 2, 3, "a", "-1"])
                         .error_level(ErrorLevel.IGNORE)
                         .all_match(lambda x: int(x) > 0))

    def test_any_match_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, "a", 3]).any_match(lambda x: int(x) > 2)

    def test_any_match_ignore(self):
        self.assertTrue(self.stream([1, 2, 3, "a", "-1"])
                        .error_level(ErrorLevel.IGNORE)
                        .any_match(lambda x: int(x) < 0))

    def test_for_each_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a"]).for_each(int)

    def test_for_each_ignore(self):
        self.stream([1, 2, 3, "a"]).error_level(ErrorLevel.IGNORE).for_each(int)

    def test_none_match_raise(self):
        with self.assertRaises(ValueError):
            self.stream([1, 2, 3, "a"]).none_match(lambda x: int(x) < 0)

    def test_none_match_ignore(self):
        self.assertFalse(self.stream([1, 2, 3, "a", "-1"])
                         .error_level(ErrorLevel.IGNORE)
                         .none_match(lambda x: int(x) < 0))

    def test_reduce_raise(self):
        with self.assertRaises(TypeError):
            self.stream([1, 2, 3, "a"]).reduce(lambda x, y: x + y)

    def test_reduce_ignore(self):
        self.assertEqual(self.stream([1, 2, 3, "a"]).error_level(ErrorLevel.IGNORE)
                         .reduce(lambda x, y: x + y).get(), 6)

    def test_different_error_level(self):
        with self.assertRaises(ValueError) as cm:
            self.stream([1, 2, 3, "a", NoToString()])\
                .error_level(ErrorLevel.IGNORE)\
                .map_to_str() \
                .error_level(ErrorLevel.RAISE) \
                .map_to_int() \
                .to_list()

        self.assertEqual(str(cm.exception), "invalid literal for int() with base 10: 'a'")
