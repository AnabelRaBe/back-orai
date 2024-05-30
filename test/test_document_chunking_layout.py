import pytest
from backend.utilities.document_chunking.Layout import LayoutDocumentChunking
from backend.utilities.common.SourceDocument import SourceDocument
from backend.utilities.document_chunking.Strategies import ChunkingSettings

class TestLayoutDocumentChunking:
    def test_chunk_method_processes_documents_fixed_import(self):

        # Initialize the LayoutDocumentChunking class
        layout_chunking = LayoutDocumentChunking()

        # Create a list of SourceDocument objects
        documents = [
            SourceDocument(
                content="Sample content 1",
                source="http://example.com/doc1",
                offset=0,
                page_number=1,
                global_business="Sample business",
                divisions_and_areas="Sample divisions",
                tags=["tag1", "tag2"],
                region="Sample region",
                country="Sample country",
                language="English",
                year="2022",
                period="Q1",
                importance="High",
                security="Confidential",
                origin="Sample origin",
                domain="Sample domain"
            ),
            SourceDocument(
                content="Sample content 2",
                source="http://example.com/doc2",
                offset=0,
                page_number=1,
                global_business="Sample business",
                divisions_and_areas="Sample divisions",
                tags=["tag1", "tag2"],
                region="Sample region",
                country="Sample country",
                language="English",
                year="2022",
                period="Q1",
                importance="High",
                security="Confidential",
                origin="Sample origin",
                domain="Sample domain"
            )
        ]

        # Invoke the chunk method of LayoutDocumentChunking class
        chunked_documents = layout_chunking.chunk(documents, ChunkingSettings({"strategy": "layout", "size": 100, "overlap": 10}))

        # Assert the output is a list and has the same number of documents
        assert isinstance(chunked_documents, list)
        assert len(chunked_documents) == len(documents)
        for doc in chunked_documents:
            assert isinstance(doc, SourceDocument)

        # Test with an empty list of SourceDocuments to ensure no errors and an empty list is returned
    def test_chunk_method_with_empty_list(self):

        # Initialize the LayoutDocumentChunking class
        layout_chunking = LayoutDocumentChunking()

        # Create an empty list of SourceDocument objects
        documents = []

        # Invoke the chunk method of LayoutDocumentChunking class with an empty list
        chunked_documents = layout_chunking.chunk(documents, ChunkingSettings({"strategy": "layout", "size": 100, "overlap": 10}))

        # Assert the output is an empty list
        assert isinstance(chunked_documents, list)
        assert len(chunked_documents) == 0