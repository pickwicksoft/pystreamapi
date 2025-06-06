# pylint: disable=not-context-manager
from types import GeneratorType
from unittest import TestCase
from unittest.mock import patch, mock_open

from _loaders.file_test import OPEN, PATH_EXISTS, PATH_ISFILE
from pystreamapi.loaders import yaml

file_content = """
---
- attr1: 1
  attr2: 2.0
- attr1:
  - attr1: a
  attr2: b
"""
file_path = 'path/to/data.yaml'


class TestYamlLoader(TestCase):

    def test_yaml_loader_from_file(self):
        with (patch(OPEN, mock_open(read_data=file_content)),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
            data = yaml(file_path)
            self._check_extracted_data(data)

    def test_yaml_loader_is_iterable(self):
        with (patch(OPEN, mock_open(read_data=file_content)),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
            data = yaml(file_path)
            self.assertEqual(len(list(iter(data))), 2)

    def test_yaml_loader_with_empty_file(self):
        with (patch(OPEN, mock_open(read_data="")),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
            data = yaml(file_path)
            self.assertEqual(len(list(data)), 0)

    def test_yaml_loader_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            yaml('path/to/invalid.yaml')

    def test_yaml_loader_with_no_file(self):
        with self.assertRaises(ValueError):
            yaml('../')

    def test_yaml_loader_from_string(self):
        data = yaml(file_content, read_from_src=True)
        self._check_extracted_data(data)

    def test_yaml_loader_from_empty_string(self):
        self.assertEqual(list(yaml('', read_from_src=True)), [])

    def test_yaml_loader_is_lazy(self):
        with (patch(OPEN, mock_open(read_data=file_content)),
              patch(PATH_EXISTS, return_value=True),
              patch(PATH_ISFILE, return_value=True)):
            data = yaml(file_path)
            self.assertIsInstance(data, GeneratorType)

    def _check_extracted_data(self, data):
        first = next(data)
        self.assertEqual(first.attr1, 1)
        self.assertIsInstance(first.attr1, int)
        self.assertEqual(first.attr2, 2.0)
        self.assertIsInstance(first.attr2, float)
        second = next(data)
        self.assertIsInstance(second.attr1, list)
        self.assertEqual(second.attr1[0].attr1, 'a')
        self.assertRaises(StopIteration, next, data)
