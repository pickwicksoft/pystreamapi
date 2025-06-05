from typing import Callable


class Process:
    """Represents a Callable with arguments to pass in. Used with the Queue"""

    def __init__(self, work: Callable, arg=None):
        """
        The class representing a function to be executed lazy.

        :param work: the function or executable (normally with object)
        :param arg: the argument to be passed to the function
        """
        self.__work = work
        self.__arg = arg

    def exec(self):
        """Run the callable in the process"""
        if self.__arg is not None:
            self.__work(self.__arg)
        else:
            self.__work()

    def has_name(self, name):
        """Check if process is method of name"""
        return self.__work.__name__ == name.__name__
