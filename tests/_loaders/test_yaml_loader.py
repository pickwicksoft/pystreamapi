# pylint: disable=not-context-manager
from types import GeneratorType
from unittest import TestCase

import yaml as yaml_lib

from _loaders.file_test import LoaderTestBase
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


class TestYamlLoader(LoaderTestBase, TestCase):

    def test_yaml_loader_from_file(self):
        with self.mock_file(file_content):
            self._check_extracted_data(yaml(file_path))

    def test_yaml_loader_is_iterable(self):
        with self.mock_file(file_content):
            self.assertEqual(len(list(iter(yaml(file_path)))), 2)

    def test_yaml_loader_with_empty_file(self):
        with self.mock_file(""):
            self.assertEqual(len(list(yaml(file_path))), 0)

    def test_yaml_loader_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            yaml('path/to/invalid.yaml')

    def test_yaml_loader_with_no_file(self):
        with self.assertRaises(ValueError):
            yaml('../')

    def test_yaml_loader_from_string(self):
        self._check_extracted_data(yaml(file_content, read_from_src=True))

    def test_yaml_loader_from_empty_string(self):
        self.assertEqual(list(yaml('', read_from_src=True)), [])

    def test_yaml_loader_is_lazy(self):
        with self.mock_file(file_content):
            self.assertIsInstance(yaml(file_path), GeneratorType)

    def test_yaml_loader_with_malformed_yaml(self):
        with self.assertRaises(yaml_lib.YAMLError):
            list(yaml("key: : invalid", read_from_src=True))

    def test_yaml_loader_skips_null_document(self):
        """Test that a null/~ document (falsy) is silently skipped."""
        with self.mock_file("~"):
            self.assertEqual(list(yaml(file_path)), [])
        self.assertEqual(list(yaml("~", read_from_src=True)), [])

    def test_yaml_loader_skips_empty_document_in_stream(self):
        """Test that an empty document in a multi-document stream is silently skipped."""
        content = "---\n- attr1: 1\n---\n"  # second document is empty
        with self.mock_file(content):
            self.assertEqual(len(list(yaml(file_path))), 1)
        self.assertEqual(len(list(yaml(content, read_from_src=True))), 1)

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
        self.assertIsInstance(second.attr1, list)
        self.assertEqual(second.attr1[0].attr1, 'a')

        self.assertRaises(StopIteration, next, data)
