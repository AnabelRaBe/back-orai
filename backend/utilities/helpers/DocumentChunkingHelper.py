"""
This class handles document chunking operations.
"""
from typing import List
from urllib.parse import urlparse
from langchain.docstore.document import Document
from ..document_chunking import get_document_chunker, ChunkingSettings, ChunkingStrategy

class DocumentChunking:
    """
    Class for chunking documents.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass

    def chunk(self, documents: List[Document], chunking: ChunkingSettings) -> List[Document]:
        """
        Chunk the given documents.
        Parameters:
            documents (List[Document]): A list of documents to chunk.
            chunking (ChunkingSettings): The chunking settings.
        Returns:
            List[Document]: A list of chunked documents.
        Raises:
            Exception: If the chunking strategy is unknown.
        """
        chunker = get_document_chunker(chunking.chunking_strategy.value)
        if chunker is None:
            raise Exception(f"Unknown chunking strategy: {chunking.chunking_strategy.value}")
        return chunker.chunk(documents, chunking)
