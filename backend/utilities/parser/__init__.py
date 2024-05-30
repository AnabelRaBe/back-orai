"""
Defines an abstract base class for parsers.
"""
from abc import ABC, abstractmethod

class ParserBase(ABC):
    """
    Abstract base class for parsers.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass

    @abstractmethod
    def parse(self, input: dict, **kwargs: dict) -> dict:
        """
        Abstract method to parse input data.
        Parameters:
            input (dict): The input data to be parsed.
            **kwargs (dict): Additional keyword arguments for parsing.
        Returns:
            dict: The parsed data.
        """
        pass
