"""
This module defines an enumeration class `ChunkingStrategy` for specifying different chunking strategies, including 'layout' and 'page'. 
It also provides a function `get_document_chunker` to retrieve the appropriate document chunker based on the selected strategy. 
Additionally, it contains a class `ChunkingSettings` for managing chunking settings.
"""
from enum import Enum

class ChunkingStrategy(Enum):
    """
    Enumeration class for chunking strategies.
    """
    layout = 'layout'
    page = 'page'

def get_document_chunker(chunking_strategy: str):
    """
    Get the document chunker based on the specified strategy.
    Parameters:
        chunking_strategy (str): The selected chunking strategy.
    Returns:
        object: An instance of the document chunker.
    Raises:
        Exception: If the chunking strategy is unknown.
    """
    if chunking_strategy == ChunkingStrategy.layout.value:
        # Importing LayoutDocumentChunking class dynamically
        from .Layout import LayoutDocumentChunking  
        return LayoutDocumentChunking()
    elif chunking_strategy == ChunkingStrategy.page.value:
        # Importing PageDocumentChunking class dynamically
        from .Page import PageDocumentChunking  
        return PageDocumentChunking()
    # elif chunking_strategy == ChunkingStrategy.FIXED_SIZE_OVERLAP.value:
    #     from .FixedSizeOverlap import FixedSizeOverlapDocumentChunking
    #     return FixedSizeOverlapDocumentChunking()
    # elif chunking_strategy == ChunkingStrategy.PARAGRAPH.value:
    #     from .Paragraph import ParagraphDocumentChunking
    #     return ParagraphDocumentChunking()
    else:
        raise ValueError(f"Unknown chunking strategy: {chunking_strategy}")

class ChunkingSettings:
    """
    Class for managing chunking settings.
    """
    def __init__(self, chunking: dict):
        """
        Initialize chunking settings.
        Parameters:
            chunking (dict): A dictionary containing chunking settings.
        """
        self.chunking_strategy = ChunkingStrategy(chunking['strategy'])
        self.chunk_size = chunking['size']
        self.chunk_overlap = chunking['overlap']
