"""
Abstract base class for document loading.
"""
from typing import List
from abc import ABC, abstractmethod
from ..common.SourceDocument import SourceDocument

class DocumentLoadingBase(ABC):
    """
    Abstract base class for document loading.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass
    
    @abstractmethod
    def load(self, document_url: str, metadata: dict) -> List[SourceDocument]:
        """
        Abstract method to load documents.
        Parameters:
            document_url (str): The URL of the document to load.
            metadata (dict): Additional metadata for loading.
        Returns:
            List[SourceDocument]: A list of loaded source documents.
        """
        pass