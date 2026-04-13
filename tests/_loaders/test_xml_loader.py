# pylint: disable=not-context-manager
from xml.etree.ElementTree import ParseError

from _loaders.file_test import LoaderTestBase
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


class TestXmlLoader(LoaderTestBase):

    def test_xml_loader_from_file_children(self):
        with self.mock_file(file_content):
            data = xml(file_path)

            try:
                first = next(data)
            except StopIteration:
                return
            self.assertEqual(first.salary, 80000)
            self.assertIsInstance(first.salary, int)

            try:
                second = next(data)
            except StopIteration:
                return
            self.assertEqual(second.child.name, "Frank")
            self.assertIsInstance(second.child.name, str)

            try:
                third = next(data)
            except StopIteration:
                return
            self.assertEqual(third.cars.car[0], 'Bugatti')
            self.assertIsInstance(third.cars.car[0], str)

            self.assertRaises(StopIteration, next, data)

    def test_xml_loader_from_file_no_children_false(self):
        with self.mock_file(file_content):
            data = xml(file_path, retrieve_children=False)

            try:
                first = next(data)
            except StopIteration:
                return

            self.assertEqual(first.employee[0].salary, 80000)
            self.assertIsInstance(first.employee[0].salary, int)
            self.assertEqual(first.employee[1].child.name, "Frank")
            self.assertIsInstance(first.employee[1].child.name, str)
            self.assertEqual(first.founder.cars.car[0], 'Bugatti')
            self.assertIsInstance(first.founder.cars.car[0], str)

            self.assertRaises(StopIteration, next, data)

    def test_xml_loader_no_casting(self):
        with self.mock_file(file_content):
            data = xml(file_path, cast_types=False)

            try:
                first = next(data)
            except StopIteration:
                pass
            self.assertEqual(first.salary, '80000')
            self.assertIsInstance(first.salary, str)

            try:
                second = next(data)
            except StopIteration:
                pass
            self.assertEqual(second.child.name, "Frank")
            self.assertIsInstance(second.child.name, str)

            try:
                third = next(data)
            except StopIteration:
                pass
            self.assertEqual(third.cars.car[0], 'Bugatti')
            self.assertIsInstance(third.cars.car[0], str)

            self.assertRaises(StopIteration, next, data)

    def test_xml_loader_is_iterable(self):
        with self.mock_file(file_content):
            data = xml(file_path)
            self.assertEqual(len(list(iter(data))), 3)

    def test_xml_loader_with_empty_file(self):
        with self.mock_file(''):
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

        try:
            first = next(data)
        except StopIteration:
            pass
        self.assertEqual(first.salary, 80000)
        self.assertIsInstance(first.salary, int)

        try:
            second = next(data)
        except StopIteration:
            pass
        self.assertEqual(second.child.name, "Frank")
        self.assertIsInstance(second.child.name, str)

        try:
            third = next(data)
        except StopIteration:
            pass
        self.assertEqual(third.cars.car[0], 'Bugatti')
        self.assertIsInstance(third.cars.car[0], str)

        self.assertRaises(StopIteration, next, data)

    def test_xml_loader_from_empty_string(self):
        with self.assertRaises(ParseError):
            list(xml('', read_from_src=True))
