from contextlib import contextmanager
from unittest.mock import patch, mock_open

OPEN = 'builtins.open'
PATH_EXISTS = 'os.path.exists'
PATH_ISFILE = 'os.path.isfile'


class LoaderTestBase:
    """Base class for loader tests with a shared file-mocking utility."""

    @contextmanager
    def mock_file(self, content="", exists=True, is_file=True):
        """Context manager for mocking file operations.

        Args:
            content: The content of the mocked file
            exists: Whether the file exists
            is_file: Whether the path points to a file
        """
        with patch(OPEN, mock_open(read_data=content)):
            with patch(PATH_EXISTS, return_value=exists):
                with patch(PATH_ISFILE, return_value=is_file):
                    yield
