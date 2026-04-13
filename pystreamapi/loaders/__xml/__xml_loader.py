import io
from typing import Iterator, Any

try:
    from defusedxml import ElementTree
except ImportError as exc:
    raise ImportError(
        "Please install the xml_loader extra dependency to use the xml loader."
    ) from exc
from collections import namedtuple
from pystreamapi.loaders.__loader_utils import LoaderUtils


def xml(src: str, read_from_src=False, retrieve_children=True, cast_types=True,
        encoding="utf-8") -> Iterator[Any]:
    """
    Loads XML data from either a path or a string and converts it into a list of namedtuples.
    Warning: This method isn't safe against malicious XML trees. Parse only safe XML from sources
    you trust.

    Returns:
        An iterator with namedtuples, where each namedtuple represents an XML element.
        :param retrieve_children: If true, the children of the root element are used as stream
        elements.
        :param encoding: The encoding of the XML file.
        :param src: Either the path to an XML file or an XML string.
        :param read_from_src: If True, src is treated as an XML string. If False, src is treated as
            a path to an XML file.
        :param cast_types: Set as False to disable casting of values to int, bool or float.
    """
    if read_from_src:
        return _lazy_parse_xml_string(src, retrieve_children, cast_types)

    path = LoaderUtils.validate_path(src)
    return _lazy_parse_xml_file(path, encoding, retrieve_children, cast_types)


def _lazy_parse_xml_file(file_path: str, encoding: str,
                         retrieve_children: bool, cast_types: bool) -> Iterator[Any]:
    """Lazily parse an XML file using iterparse, yielding namedtuples without reading all at once."""
    def generator():
        """Generator that streams XML elements from the file and yields namedtuples lazily."""
        # skipcq: PTC-W6004
        with open(file_path, mode='r', encoding=encoding) as xmlfile:
            yield from _iterparse_xml(xmlfile, retrieve_children, cast_types)

    return generator()


def _lazy_parse_xml_string(xml_string: str, retrieve_children: bool,
                           cast_types: bool) -> Iterator[Any]:
    """Lazily parse an XML string using iterparse, yielding namedtuples without a full DOM build."""
    def generator():
        """Generator that streams XML elements from a string source and yields namedtuples."""
        yield from _iterparse_xml(io.StringIO(xml_string), retrieve_children, cast_types)

    return generator()


def _iterparse_xml(source, retrieve_children: bool, cast_types: bool) -> Iterator[Any]:
    """Drive iterparse over *source* and yield namedtuples incrementally.

    When *retrieve_children* is True each direct child of the root element is
    converted and yielded as soon as its closing tag is encountered; the child
    is then removed from the root so that memory is freed immediately.

    When *retrieve_children* is False the entire document is consumed and the
    root element is converted and yielded once.
    """
    depth = 0
    root = None
    context = ElementTree.iterparse(source, events=('start', 'end'))

    for event, elem in context:
        if event == 'start':
            depth += 1
            if root is None:
                root = elem
        else:  # 'end'
            depth -= 1
            if retrieve_children:
                if depth == 1:
                    yield __parse_xml(elem, cast_types)
                    root.remove(elem)
            else:
                if depth == 0:
                    yield __parse_xml(root, cast_types)
                    return


def __parse_xml(element, cast_types: bool):
    """Parse XML element and convert it into a namedtuple."""
    if len(element) == 0:
        return __parse_empty_element(element, cast_types)
    if len(element) == 1:
        return __parse_single_element(element, cast_types)
    return __parse_multiple_elements(element, cast_types)


def __parse_empty_element(element, cast_types: bool):
    """Parse XML element without children and convert it into a namedtuple."""
    return LoaderUtils.try_cast(element.text) if cast_types else element.text


def __parse_single_element(element, cast_types: bool):
    """Parse XML element with a single child and convert it into a namedtuple."""
    sub_element = element[0]
    sub_item = __parse_xml(sub_element, cast_types)
    Item = namedtuple(element.tag, [sub_element.tag])
    return Item(sub_item)


def __parse_multiple_elements(element, cast_types: bool):
    """Parse XML element with multiple children and convert it into a namedtuple."""
    tag_dict = {}
    for e in element:
        if e.tag not in tag_dict:
            tag_dict[e.tag] = []
        tag_dict[e.tag].append(__parse_xml(e, cast_types))
    filtered_dict = __filter_single_items(tag_dict)
    Item = namedtuple(element.tag, filtered_dict.keys())
    return Item(*filtered_dict.values())


def __filter_single_items(tag_dict):
    """Filter out single-item lists from a dictionary."""
    return {key: value[0] if len(value) == 1 else value for key, value in tag_dict.items()}

