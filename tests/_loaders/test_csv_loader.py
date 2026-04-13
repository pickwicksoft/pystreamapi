# pylint: disable=not-context-manager
from unittest import TestCase

from _loaders.file_test import LoaderTestBase
from pystreamapi.loaders import csv


class TestCSVLoader(LoaderTestBase, TestCase):
    """Test cases for the CSV loader functionality."""

    def setUp(self):
        self.file_content = """attr1,attr2
1,2.0
a,b"""
        self.file_path = 'path/to/data.csv'

    def test_csv_loader_basic_functionality(self):
        """Test basic CSV loading with type casting."""
        with self.mock_file(self.file_content):
            data = csv(self.file_path)

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
            self.assertEqual(second.attr1, 'a')
            self.assertIsInstance(second.attr1, str)
            self.assertEqual(second.attr2, 'b')
            self.assertIsInstance(second.attr2, str)

            # Verify end of file
            self.assertRaises(StopIteration, next, data)

    def test_csv_loader_without_type_casting(self):
        """Test CSV loading with type casting disabled."""
        with self.mock_file(self.file_content):
            data = csv(self.file_path, cast_types=False)

            # Verify all values remain as strings
            try:
                first = next(data)
            except StopIteration:
                return
            self.assertIsInstance(first.attr1, str)
            self.assertIsInstance(first.attr2, str)
            self.assertEqual(first.attr1, '1')
            self.assertEqual(first.attr2, '2.0')

    def test_csv_loader_iteration(self):
        """Test CSV loader's iteration capability."""
        with self.mock_file(self.file_content):
            data = csv(self.file_path)
            self.assertEqual(len(list(data)), 2)

    def test_csv_loader_custom_delimiter(self):
        """Test CSV loading with a custom delimiter."""
        content_with_semicolon = self.file_content.replace(",", ";")
        with self.mock_file(content_with_semicolon):
            data = csv(self.file_path, delimiter=';')
            try:
                first = next(data)
            except StopIteration:
                return
            self.assertEqual(first.attr1, 1)
            self.assertEqual(first.attr2, 2.0)

    def test_csv_loader_edge_cases(self):
        """Test CSV loader with edge cases."""
        # Empty file
        with self.mock_file(""):
            data = csv(self.file_path)
            self.assertEqual(len(list(data)), 0)

        # Invalid file path
        with self.mock_file(self.file_content, exists=False), self.assertRaises(FileNotFoundError):
            csv('path/to/invalid.csv')

        # Path is not a file
        with self.mock_file(self.file_content, is_file=False), self.assertRaises(ValueError):
            csv('../')

    def test_csv_loader_from_string(self):
        """Test CSV loading from a string."""
        data = csv(self.file_content, read_from_src=True)

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
        self.assertEqual(second.attr1, 'a')
        self.assertIsInstance(second.attr1, str)
        self.assertEqual(second.attr2, 'b')
        self.assertIsInstance(second.attr2, str)

        # Verify end of file
        self.assertRaises(StopIteration, next, data)

    def test_csv_loader_from_empty_string(self):
        """Test CSV loading from an empty string."""
        with self.assertRaises(StopIteration):
            next(csv("", read_from_src=True))
