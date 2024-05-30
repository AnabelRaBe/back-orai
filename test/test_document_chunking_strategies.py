import pytest
from backend.utilities.document_chunking.Strategies import get_document_chunker, ChunkingStrategy
from backend.utilities.document_chunking.Layout import LayoutDocumentChunking
from backend.utilities.document_chunking.Page import PageDocumentChunking
def test_get_document_chunker():
    # Test case for 'layout' strategy
    chunker = get_document_chunker(ChunkingStrategy.layout.value)
    assert isinstance(chunker, LayoutDocumentChunking)

    # Test case for 'page' strategy
    chunker = get_document_chunker(ChunkingStrategy.page.value)
    assert isinstance(chunker, PageDocumentChunking)

    # Test case for unknown strategy
    with pytest.raises(Exception):
        get_document_chunker('unknown_strategy')