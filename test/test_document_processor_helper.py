import pytest
from unittest.mock import MagicMock, patch
from backend.utilities.helpers.DocumentProcessorHelper import Processor, DocumentProcessor

@pytest.fixture
def document_processor():
    return DocumentProcessor()

# def test_process_success(document_processor):
#     # Mock the dependencies
#     source_url = "https://example.com/documents"
#     processors = [Processor("type1", MagicMock(), MagicMock())]
#     index_name = "index_name"
#     metadata = {"key": "value"}

#     # Mock the AzureSearchHelper and its methods
#     azure_search_helper_mock = MagicMock()
#     azure_search_helper_mock.get_vector_store.return_value = MagicMock()
#     vector_store_mock = azure_search_helper_mock.get_vector_store.return_value
#     vector_store_mock.add_documents.return_value = "success"

#     # Set the mocked AzureSearchHelper
#     document_processor.vector_store_helper = azure_search_helper_mock

#     # Call the process method
#     result = document_processor.process(source_url, processors, index_name, metadata)

#     # Assert the result
#     assert result == "success"

def test_process_error(document_processor):
    # Mock the dependencies
    source_url = "https://example.com/documents"
    processors = [Processor("type1", MagicMock(), MagicMock())]
    index_name = "index_name"
    metadata = {"key": "value"}

    # Mock the AzureSearchHelper and its methods
    azure_search_helper_mock = MagicMock()
    azure_search_helper_mock.get_vector_store.return_value = MagicMock()
    vector_store_mock = azure_search_helper_mock.get_vector_store.return_value
    vector_store_mock.add_documents.side_effect = Exception("Error adding embeddings")

    # Set the mocked AzureSearchHelper
    document_processor.vector_store_helper = azure_search_helper_mock

    # Call the process method and assert that it raises an exception
    with pytest.raises(Exception):
        document_processor.process(source_url, processors, index_name, metadata)