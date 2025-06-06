# pylint: disable=not-context-manager
from contextlib import contextmanager
from unittest import TestCase
from unittest.mock import patch, mock_open
from xml.etree.ElementTree import ParseError

from _loaders.file_test import OPEN, PATH_EXISTS, PATH_ISFILE
from pystreamapi.loaders import xml

file_content = """
<employees>
    <employee>
        <name>John Doe</name>
        <salary>80000</salary>
    </employee>
    <employee>
        <name>Alice Smith</name>
        <child>
            <name>Frank</name>
        </child>
    </employee>
    <founder>
        <cars>
            <car>Bugatti</car>
            <car>Mercedes</car>
        </cars>
    </founder>
</employees>
"""
file_path = 'path/to/data.xml'


class TestXmlLoader(TestCase):

    @contextmanager
    def mock_csv_file(self, content=None, exists=True, is_file=True):
        """Context manager for mocking CSV file operations.

        Args:
            content: The content of the mocked file
            exists: Whether the file exists
            is_file: Whether the path points to a file
        """
        content = content if content is not None else self.file_content
        with (patch(OPEN, mock_open(read_data=content)),
              patch(PATH_EXISTS, return_value=exists),
              patch(PATH_ISFILE, return_value=is_file)):
            yield

    def test_xml_loader_from_file_children(self):
        with self.mock_csv_file(file_content):
            data = xml(file_path)

            first = next(data)
            self.assertEqual(first.salary, 80000)
            self.assertIsInstance(first.salary, int)

            second = next(data)
            self.assertEqual(second.child.name, "Frank")
            self.assertIsInstance(second.child.name, str)

            third = next(data)
            self.assertEqual(third.cars.car[0], 'Bugatti')
            self.assertIsInstance(third.cars.car[0], str)

            self.assertRaises(StopIteration, next, data)

    def test_xml_loader_from_file_no_children_false(self):
        with self.mock_csv_file(file_content):
            data = xml(file_path, retrieve_children=False)

            first = next(data)
            self.assertEqual(first.employee[0].salary, 80000)
            self.assertIsInstance(first.employee[0].salary, int)
            self.assertEqual(first.employee[1].child.name, "Frank")
            self.assertIsInstance(first.employee[1].child.name, str)
            self.assertEqual(first.founder.cars.car[0], 'Bugatti')
            self.assertIsInstance(first.founder.cars.car[0], str)

            self.assertRaises(StopIteration, next, data)

    def test_xml_loader_no_casting(self):
        with self.mock_csv_file(file_content):
            data = xml(file_path, cast_types=False)

            first = next(data)
            self.assertEqual(first.salary, '80000')
            self.assertIsInstance(first.salary, str)

            second = next(data)
            self.assertEqual(second.child.name, "Frank")
            self.assertIsInstance(second.child.name, str)

            third = next(data)
            self.assertEqual(third.cars.car[0], 'Bugatti')
            self.assertIsInstance(third.cars.car[0], str)

            self.assertRaises(StopIteration, next, data)

    def test_xml_loader_is_iterable(self):
        with self.mock_csv_file(file_content):
            data = xml(file_path)
            self.assertEqual(len(list(iter(data))), 3)

    def test_xml_loader_with_empty_file(self):
        with self.mock_csv_file(''):
            data = xml(file_path)
            self.assertRaises(ParseError, next, data)

    def test_xml_loader_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            xml('path/to/invalid.xml')

    def test_xml_loader_with_no_file(self):
        with self.assertRaises(ValueError):
            xml('../')

    def test_xml_loader_from_string(self):
        data = xml(file_content, read_from_src=True)

        first = next(data)
        self.assertEqual(first.salary, 80000)
        self.assertIsInstance(first.salary, int)

        second = next(data)
        self.assertEqual(second.child.name, "Frank")
        self.assertIsInstance(second.child.name, str)

        third = next(data)
        self.assertEqual(third.cars.car[0], 'Bugatti')
        self.assertIsInstance(third.cars.car[0], str)

        self.assertRaises(StopIteration, next, data)

    def test_xml_loader_from_empty_string(self):
        with self.assertRaises(ParseError):
            list(xml('', read_from_src=True))
