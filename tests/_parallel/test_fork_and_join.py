import os
from unittest import TestCase
from functools import reduce as seq_reduce

from pystreamapi._parallel.fork_and_join import Parallelizer


class TestForkAndJoin(TestCase):

    def setUp(self):
        self.parallelizer = Parallelizer()

    def test_fork_short_src(self):
        self.parallelizer.set_source([1, 2])
        res = self.parallelizer.fork()
        self.assertListEqual(res, [[1], [2]])

    def test_fork_short_src_min_two(self):
        self.parallelizer.set_source([1, 2])
        res = self.parallelizer.fork(2)
        self.assertListEqual(res, [[1, 2]])

    def test_fork_src_too_small(self):
        self.parallelizer.set_source([1])
        res = self.parallelizer.fork(2)
        self.assertListEqual(res, [[1]])

    def test_fork_long_src(self):
        self.parallelizer.set_source(list(range(100)))
        res = self.parallelizer.fork()
        self.assertEqual(len(res), os.cpu_count() - 2 if os.cpu_count() > 2 else os.cpu_count())

    def test_fork_src_empty(self):
        self.parallelizer.set_source([])
        res = self.parallelizer.fork()
        self.assertListEqual(res, [])

    def test_fork_src_min_items_invalid(self):
        self.parallelizer.set_source([])
        self.assertRaises(ValueError, lambda: self.parallelizer.fork(0))
        self.assertRaises(ValueError, lambda: self.parallelizer.fork(-1))

    def test_reduce(self):
        self.parallelizer.set_source([1, 2, 3, 4, 5])
        result = self.parallelizer.reduce(lambda x, y: x + y)
        self.assertEqual(result, 15)

    def test_reduce_empty(self):
        self.parallelizer.set_source([])
        result = self.parallelizer.reduce(lambda x, y: x + y)
        self.assertEqual(result, [])

    def test_reduce_one_element(self):
        self.parallelizer.set_source([1])
        result = self.parallelizer.reduce(lambda x, y: x + y)
        self.assertEqual(result, [1])

    def test_reduce_big_source(self):
        self.parallelizer.set_source(list(range(1000)))
        result = self.parallelizer.reduce(lambda x, y: x + y)
        self.assertEqual(result, 499_500)

    def test_parallel_vs_sequential_reduce(self):
        self.parallelizer.set_source(list(range(1000)))
        parallel = self.parallelizer.reduce(lambda x, y: x + y)
        sequential = seq_reduce(lambda x, y: x + y, list(range(1000)))
        self.assertEqual(parallel, sequential)

    def test_filter(self):
        self.parallelizer.set_source([1, 2, "3", None])
        result = self.parallelizer.filter(lambda x: x is not None)
        self.assertListEqual([1, 2, "3"], result)

    def test_filter_empty(self):
        self.parallelizer.set_source([])
        result = self.parallelizer.filter(lambda x: x is not None)
        self.assertListEqual([], result)

    def test_filter_one(self):
        self.parallelizer.set_source([None])
        result = self.parallelizer.filter(lambda x: x is not None)
        self.assertListEqual([], result)

    def test_limit(self):
        self.parallelizer.set_source([1, 2, 3, 4, 5])
        result = list(self.parallelizer.limit(3))
        self.assertListEqual(result, [1, 2, 3])

    def test_limit_empty(self):
        self.parallelizer.set_source([])
        result = list(self.parallelizer.limit(3))
        self.assertListEqual(result, [])

    def test_limit_one_element(self):
        self.parallelizer.set_source([1])
        result = list(self.parallelizer.limit(3))
        self.assertListEqual(result, [1])

    def test_limit_infinite_source(self):
        def infinite_gen():
            i = 0
            while True:
                yield i
                i += 1

        self.parallelizer.set_source(infinite_gen())
        result = list(self.parallelizer.limit(5))
        self.assertListEqual(result, [0, 1, 2, 3, 4])

    def test_filter_infinite_source(self):
        def infinite_gen():
            i = 0
            while True:
                yield i
                i += 1

        self.parallelizer.set_source(infinite_gen())
        result = self.parallelizer.filter(lambda x: x % 2 == 0)
        limited_result = list(self.parallelizer.limit(5))
        self.assertListEqual(limited_result, [0, 2, 4, 6, 8])
