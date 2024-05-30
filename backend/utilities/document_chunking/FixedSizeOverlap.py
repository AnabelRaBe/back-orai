"""
This module provides a class for chunking documents into fixed-size overlapping chunks.
Attributes:FixedSizeOverlapDocumentChunking: A class for chunking documents into fixed-size overlapping chunks.
"""
from typing import List
from .DocumentChunkingBase import DocumentChunkingBase
from langchain.text_splitter import TokenTextSplitter
from .Strategies import ChunkingSettings
from ..common.SourceDocument import SourceDocument

class FixedSizeOverlapDocumentChunking(DocumentChunkingBase):
    """
    Class for chunking documents using a fixed size overlap strategy.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass
        
    def chunk(self, documents: List[SourceDocument], chunking: ChunkingSettings) -> List[SourceDocument]:    
        """
        Chunk the documents using the fixed size overlap strategy.
        Parameters:
            documents (List[SourceDocument]): The list of source documents to chunk.
            chunking (ChunkingSettings): The chunking settings.
        Returns:
            List[SourceDocument]: The list of chunked source documents.
        """
        full_document_content = "".join(list(map(lambda document: document.content, documents)))
        document_url = documents[0].source
        splitter = TokenTextSplitter.from_tiktoken_encoder(chunk_size=chunking.chunk_size, chunk_overlap=chunking.chunk_overlap)
        chunked_content_list = splitter.split_text(full_document_content)
        # Create document for each chunk
        documents = []
        chunk_offset = 0
        for idx, chunked_content in enumerate(chunked_content_list):
            documents.append(
                SourceDocument.from_metadata(
                    content=chunked_content,
                    document_url=document_url,
                    metadata={"offset": chunk_offset},
                    idx=idx,
                )
            )            
            chunk_offset += len(chunked_content)
        return documents
