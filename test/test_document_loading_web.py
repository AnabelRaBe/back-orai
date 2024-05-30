import pytest
from unittest.mock import patch, MagicMock
from backend.utilities.document_loading.Web import WebDocumentLoading, SourceDocument

@pytest.fixture
def web_document_loader():
    return WebDocumentLoading()

def test_web_document_loader_load(web_document_loader):
    # Mock the WebBaseLoader and its load method
    with patch('backend.utilities.document_loading.Web.WebBaseLoader') as mocked_loader:
        mocked_document = MagicMock()
        mocked_document.page_content = "\n\n\nSample content\n\n\n"
        mocked_document.metadata = {'source': 'http://example.com'}
        
        mocked_loader.return_value.load.return_value = [mocked_document]

        # Metadata to pass to the load method
        metadata = {
            "global_business": "Tech",
            "divisions_and_areas": "R&D",
            "tags": ["innovation", "development"],
            "region": "Europe",
            "country": "Germany",
            "language": "English",
            "year": "2023",
            "period": "Q1",
            "importance": "High",
            "security": "Confidential",
            "origin": "Internal",
            "domain": "Engineering"
        }

        # Call the load method
        result = web_document_loader.load("http://example.com/document", metadata)

        # Assertions to verify the behavior
        assert len(result) == 1
        assert isinstance(result[0], SourceDocument)
        assert result[0].content == "Sample content"
        assert result[0].source == "http://example.com"
        assert result[0].global_business == "Tech"
        assert result[0].tags == "innovation, development"
        assert result[0].language == "English"