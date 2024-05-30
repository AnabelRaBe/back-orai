"""
This module contains a class for chunking documents into paragraphs.
Attributes:ParagraphDocumentChunking: A class for paragraph document chunking.
"""
from typing import List
from .DocumentChunkingBase import DocumentChunkingBase
from .Strategies import ChunkingSettings
from ..common.SourceDocument import SourceDocument

class ParagraphDocumentChunking(DocumentChunkingBase):
    """
    Class for paragraph document chunking.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass
    
    def chunk(self, documents: List[SourceDocument], chunking: ChunkingSettings) -> List[SourceDocument]:
        """
        Chunk documents using paragraph chunking strategy (not implemented yet).
        Parameters:
            documents (List[SourceDocument]): A list of source documents to chunk.
            chunking (ChunkingSettings): The chunking settings.
        Returns:
            List[SourceDocument]: A list of chunked source documents.
        Raises:
            NotImplementedError: If the chunking strategy is not implemented yet.
        """
        raise NotImplementedError("Paragraph chunking is not implemented yet")