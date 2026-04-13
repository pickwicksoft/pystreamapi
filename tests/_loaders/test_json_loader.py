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

single_object_content = """
{
  "attr1": 1,
  "attr2": 2.0
}
"""

file_path = 'path/to/data.json'


class TestJsonLoader(LoaderTestBase, TestCase):

    def test_json_loader_from_file(self):
        with self.mock_file(file_content):
            self._check_extracted_data(json(file_path))

    def test_json_loader_is_iterable(self):
        with self.mock_file(file_content):
            self.assertEqual(len(list(iter(json(file_path)))), 2)

    def test_json_loader_with_empty_file(self):
        with self.mock_file(""):
            self.assertRaises(StopIteration, next, json(file_path))

    def test_json_loader_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            json('path/to/invalid.json')

    def test_json_loader_with_no_file(self):
        with self.assertRaises(ValueError):
            json('../')

    def test_json_loader_from_string(self):
        self._check_extracted_data(json(file_content, read_from_src=True))

    def test_json_loader_from_empty_string(self):
        self.assertRaises(StopIteration, next, json("", read_from_src=True))

    def test_json_loader_single_object_from_file(self):
        """Test that a single JSON object (not array) is yielded as one namedtuple."""
        with self.mock_file(single_object_content):
            data = json(file_path)
            try:
                first = next(data)
            except StopIteration:
                self.fail("Expected one row but iterator was empty")
            self.assertEqual(first.attr1, 1)
            self.assertEqual(first.attr2, 2.0)
            self.assertRaises(StopIteration, next, data)

    def test_json_loader_single_object_from_string(self):
        """Test that a single JSON object string is yielded as one namedtuple."""
        data = json(single_object_content, read_from_src=True)
        try:
            first = next(data)
        except StopIteration:
            self.fail("Expected one row but iterator was empty")
        self.assertEqual(first.attr1, 1)
        self.assertEqual(first.attr2, 2.0)
        self.assertRaises(StopIteration, next, data)

    def _check_extracted_data(self, data):
        try:
            first = next(data)
        except StopIteration:
            self.fail("Expected first row but iterator was empty")
        self.assertEqual(first.attr1, 1)
        self.assertIsInstance(first.attr1, int)
        self.assertEqual(first.attr2, 2.0)
        self.assertIsInstance(first.attr2, float)

        try:
            second = next(data)
        except StopIteration:
            self.fail("Expected second row but iterator was exhausted after first row")
        self.assertEqual(second.attr1[0].attr1, 'a')
        self.assertIsInstance(second.attr1, list)

        self.assertRaises(StopIteration, next, data)
