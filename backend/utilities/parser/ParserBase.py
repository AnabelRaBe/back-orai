"""
This abstract base class defines the structure for parsers.
"""
from abc import ABC, abstractmethod
from typing import List
from ..common.SourceDocument import SourceDocument

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
    def parse(self, question: str, answer: str, source_documents: List[SourceDocument], **kwargs: dict) -> List[dict]:
        """
        Abstract method to parse input data.
        Parameters:
            question (str): The question to parse.
            answer (str): The answer to parse.
            source_documents (List[SourceDocument]): A list of source documents.
            **kwargs (dict): Additional keyword arguments for parsing. 
        Returns:
            List[dict]: A list of parsed data.
        """
        pass