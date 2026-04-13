# pylint: disable=not-context-manager
from types import GeneratorType
from unittest import TestCase

import tomlkit.exceptions

from _loaders.file_test import LoaderTestBase
from pystreamapi.loaders import toml

# A simple flat TOML document
file_content = """
attr1 = 1
attr2 = 2.0
nested = {attr3 = "hello"}
"""

# TOML with an array of tables (non-consistent fields across entries)
non_consistent_content = """
[[employees.employee]]
name = "John Doe"
position = "Software Engineer"
salary = 80000
children = 2

[[employees.employee]]
name = "Alice Smith"
position = "Network Administrator"
salary = 75000
children = 1

[[employees.employee]]
name = "Bob Johnson"
experience = "Database"
wage = 82000
car = "Audi"
"""

file_path = 'path/to/data.toml'


class TestTomlLoader(LoaderTestBase, TestCase):

    def test_toml_loader_from_file(self):
        with self.mock_file(file_content):
            self._check_extracted_data(toml(file_path))

    def test_toml_loader_from_string(self):
        self._check_extracted_data(toml(file_content, read_from_src=True))

    def test_toml_loader_is_iterable(self):
        with self.mock_file(file_content):
            self.assertEqual(len(list(iter(toml(file_path)))), 1)

    def test_toml_loader_is_lazy(self):
        with self.mock_file(file_content):
            self.assertIsInstance(toml(file_path), GeneratorType)

    def test_toml_loader_with_empty_file(self):
        with self.mock_file(""):
            self.assertEqual(list(toml(file_path)), [])

    def test_toml_loader_from_empty_string(self):
        self.assertEqual(list(toml("", read_from_src=True)), [])

    def test_toml_loader_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            toml('path/to/invalid.toml')

    def test_toml_loader_with_no_file(self):
        with self.assertRaises(ValueError):
            toml('../')

    def test_toml_loader_with_malformed_toml(self):
        with self.assertRaises(tomlkit.exceptions.ParseError):
            list(toml("invalid = = toml", read_from_src=True))

    def test_toml_loader_non_consistent_data(self):
        """Each [[array of tables]] entry may have different fields."""
        with self.mock_file(non_consistent_content):
            data = list(toml(file_path))
        self.assertEqual(len(data), 1)
        employees = data[0].employees.employee
        self.assertEqual(len(employees), 3)

        # First employee has name, position, salary, children
        self.assertEqual(employees[0].name, "John Doe")
        self.assertEqual(employees[0].salary, 80000)
        self.assertIsInstance(employees[0].salary, int)

        # Second employee has name, position, salary, children
        self.assertEqual(employees[1].name, "Alice Smith")
        self.assertEqual(employees[1].salary, 75000)

        # Third employee has different fields (experience, wage, car)
        self.assertEqual(employees[2].name, "Bob Johnson")
        self.assertEqual(employees[2].wage, 82000)
        self.assertEqual(employees[2].car, "Audi")

    def test_toml_loader_non_consistent_from_string(self):
        """Same as above but loading from a string."""
        data = list(toml(non_consistent_content, read_from_src=True))
        self.assertEqual(len(data), 1)
        employees = data[0].employees.employee
        self.assertEqual(len(employees), 3)
        self.assertEqual(employees[0].name, "John Doe")
        self.assertEqual(employees[2].car, "Audi")

    def test_toml_loader_native_types(self):
        """TOML is self-typed so int, float, bool values should be their native types."""
        content = "count = 42\nrate = 3.14\nflag = true\n"
        data = list(toml(content, read_from_src=True))
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item.count, 42)
        self.assertIsInstance(item.count, int)
        self.assertAlmostEqual(item.rate, 3.14)
        self.assertIsInstance(item.rate, float)
        self.assertTrue(item.flag)
        self.assertIsInstance(item.flag, bool)

    def test_toml_loader_nested_table(self):
        """Nested TOML tables are converted to nested namedtuples."""
        with self.mock_file(file_content):
            data = list(toml(file_path))
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item.nested.attr3, "hello")
        self.assertIsInstance(item.nested.attr3, str)

    def _check_extracted_data(self, data):
        try:
            first = next(data)
        except StopIteration:
            self.fail("Expected first item but iterator was empty")
        self.assertEqual(first.attr1, 1)
        self.assertIsInstance(first.attr1, int)
        self.assertAlmostEqual(first.attr2, 2.0)
        self.assertIsInstance(first.attr2, float)
        self.assertEqual(first.nested.attr3, "hello")
        self.assertIsInstance(first.nested.attr3, str)

        self.assertRaises(StopIteration, next, data)
