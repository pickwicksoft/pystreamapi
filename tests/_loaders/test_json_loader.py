# pylint: disable=not-context-manager
from unittest import TestCase
from unittest.mock import patch, mock_open

from _loaders.file_test import OPEN, PATH_EXISTS, PATH_ISFILE
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


class TestJsonLoader(TestCase):

    def test_json_loader_from_file(self):
        with (patch(OPEN, mock_open(read_data=file_content)),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
            data = json(file_path)
            self._check_extracted_data(data)

    def test_json_loader_is_iterable(self):
        with (patch(OPEN, mock_open(read_data=file_content)),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
            data = json(file_path)
            self.assertEqual(len(list(iter(data))), 2)

    def test_json_loader_with_empty_file(self):
        with (patch(OPEN, mock_open(read_data="")),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
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
        first = next(data)
        self.assertEqual(first.attr1, 1)
        self.assertIsInstance(first.attr1, int)
        self.assertEqual(first.attr2, 2.0)
        self.assertIsInstance(first.attr2, float)

        # Test second row
        second = next(data)
        self.assertEqual(second.attr1[0].attr1, 'a')
        self.assertIsInstance(second.attr1, list)

        # Verify end of file
        self.assertRaises(StopIteration, next, data)
