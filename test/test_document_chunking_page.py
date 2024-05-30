import pytest
from unittest.mock import MagicMock
from backend.utilities.document_chunking.Page import PageDocumentChunking
from backend.utilities.common.SourceDocument import SourceDocument
from backend.utilities.document_chunking.Strategies import ChunkingSettings

class TestPageDocumentChunking:
    def test_chunk(self):
        # Mocking the necessary dependencies
        documents = [
            SourceDocument(
                content="This is the first document.",
                source="https://example.com/document1",
                offset=0,
                page_number=1,
                global_business="Business1",
                divisions_and_areas=["Division1", "Area1"],
                tags=["Tag1", "Tag2"],
                region="Region1",
                country="Country1",
                language="English",
                year=2022,
                period="Q1",
                importance=1,
                security="High",
                origin="Origin1",
                domain="Domain1"
            ),
            SourceDocument(
                content="This is the second document.",
                source="https://example.com/document2",
                offset=100,
                page_number=2,
                global_business="Business2",
                divisions_and_areas=["Division2", "Area2"],
                tags=["Tag3", "Tag4"],
                region="Region2",
                country="Country2",
                language="English",
                year=2022,
                period="Q2",
                importance=2,
                security="Medium",
                origin="Origin2",
                domain="Domain2"
            )
        ]
        chunking_settings = ChunkingSettings({"strategy": "layout", "size": 100, "overlap": 10})
        page_document_chunking = PageDocumentChunking()

        # Calling the chunk method
        result = page_document_chunking.chunk(documents, chunking_settings)

        assert isinstance(result, list)
        assert len(result) == len(documents)
        for doc in result:
            assert isinstance(doc, SourceDocument)
