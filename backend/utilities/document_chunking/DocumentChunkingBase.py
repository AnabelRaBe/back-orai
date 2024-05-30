"""
Abstract base class for document chunking operations.
"""
from typing import List
from abc import ABC, abstractmethod
from ..common.SourceDocument import SourceDocument
from .Strategies import ChunkingSettings

class DocumentChunkingBase(ABC):
    """
    Abstract base class for document chunking.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass
    
    @abstractmethod
    def chunk(self, documents: List[SourceDocument], chunking: ChunkingSettings) -> List[SourceDocument]:
        """
        Abstract method to chunk documents.
        Parameters:
            documents (List[SourceDocument]): A list of source documents to chunk.
            chunking (ChunkingSettings): The chunking settings.
        Returns:
            List[SourceDocument]: A list of chunked source documents.
        """
        pass