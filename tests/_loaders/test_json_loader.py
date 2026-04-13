# pylint: disable=not-context-manager
from unittest import TestCase

from _loaders.file_test import LoaderTestBase
from pystreamapi.loaders import json

file_content = """
[
  {
    "attr1": 1,
    "attr2": 2.0
  },
  {
    "attr1": [
      {
        "attr1": "a"
      }
    ],
    "attr2": "b"
  }
]
"""
file_path = 'path/to/data.json'


class TestJsonLoader(LoaderTestBase, TestCase):

    def test_json_loader_from_file(self):
        with self.mock_file(file_content):
            data = json(file_path)
            self._check_extracted_data(data)

    def test_json_loader_is_iterable(self):
        with self.mock_file(file_content):
            data = json(file_path)
            self.assertEqual(len(list(iter(data))), 2)

    def test_json_loader_with_empty_file(self):
        with self.mock_file(""):
            data = json(file_path)
            self.assertRaises(StopIteration, next, data)

    def test_json_loader_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            json('path/to/invalid.json')

    def test_json_loader_with_no_file(self):
        with self.assertRaises(ValueError):
            json('../')

    def test_json_loader_from_string(self):
        data = json(file_content, read_from_src=True)
        self._check_extracted_data(data)

    def test_json_loader_from_empty_string(self):
        self.assertRaises(StopIteration, next, json("", read_from_src=True))

    def _check_extracted_data(self, data):
        # Test first row
        try:
            first = next(data)
        except StopIteration:
            return
        self.assertEqual(first.attr1, 1)
        self.assertIsInstance(first.attr1, int)
        self.assertEqual(first.attr2, 2.0)
        self.assertIsInstance(first.attr2, float)

        # Test second row
        try:
            second = next(data)
        except StopIteration:
            return
        self.assertEqual(second.attr1[0].attr1, 'a')
        self.assertIsInstance(second.attr1, list)

        # Verify end of file
        self.assertRaises(StopIteration, next, data)
