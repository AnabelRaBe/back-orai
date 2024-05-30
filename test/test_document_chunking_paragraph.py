import pytest
from unittest.mock import MagicMock
from backend.utilities.document_chunking.Paragraph import ParagraphDocumentChunking
from backend.utilities.common.SourceDocument import SourceDocument
from backend.utilities.document_chunking.Strategies import ChunkingSettings

class TestParagraphDocumentChunking:
    def test_chunk_not_implemented(self):
        # Arrange
        chunking = ChunkingSettings({"strategy": "layout", "size": 100, "overlap": 10})
        chunking_strategy = ParagraphDocumentChunking()
        documents = [SourceDocument("Document 1", "This is the content of document 1")]

        # Act & Assert
        with pytest.raises(NotImplementedError):
            chunking_strategy.chunk(documents, chunking)