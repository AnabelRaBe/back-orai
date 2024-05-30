import pytest
from unittest.mock import Mock
from backend.utilities.document_chunking.FixedSizeOverlap import FixedSizeOverlapDocumentChunking
from backend.utilities.document_chunking.Strategies import ChunkingSettings
from backend.utilities.common.SourceDocument import SourceDocument

class TestFixedSizeOverlapDocumentChunking:
    @pytest.fixture
    def chunking(self):
        return FixedSizeOverlapDocumentChunking()

    def test_chunk(self, chunking):
        documents = [
            SourceDocument(content="This is the first chunk.", source="https://example.com/document.pdf"),
            SourceDocument(content="This is the second chunk.", source="https://example.com/document.pdf"),
            SourceDocument(content="This is the third chunk.", source="https://example.com/document.pdf"),
        ]

        chunking_settings = ChunkingSettings({
                                'strategy': 'layout',
                                'size': 6,
                                'overlap': 0
                            })

        result = chunking.chunk(documents, chunking_settings)
        
        assert result[0].content == "This is the first chunk."
        assert result[0].source == "https://example.com/document.pdf"

        assert result[1].content == "This is the second chunk."
        assert result[1].source == "https://example.com/document.pdf"

        assert result[2].content == "This is the third chunk."
        assert result[2].source == "https://example.com/document.pdf"
        