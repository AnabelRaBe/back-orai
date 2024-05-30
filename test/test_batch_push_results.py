import pytest
from unittest.mock import patch, MagicMock
from azure.functions import EventHubEvent
from backend.BatchPushResults.__init__ import main

@pytest.fixture
def event():
    return EventHubEvent(body=b'{"filename": "test_file.txt", "index_name": "test_index", "container_name": "test_container", "metadata": "{}"}')

@patch('backend.BatchPushResults.__init__.json.loads')
@patch('backend.BatchPushResults.__init__.DocumentProcessor')
@patch('backend.BatchPushResults.__init__.AzureBlobStorageClient')
def test_main(mock_blob_client, mock_document_processor, mock_json_loads, event):
    mock_json_loads.return_value = {"filename": "test_file.txt", "index_name": "test_index", "container_name": "test_container", "metadata": "{}"}
    mock_document_processor_instance = MagicMock()
    mock_document_processor.return_value = mock_document_processor_instance
    mock_blob_client_instance = MagicMock()
    mock_blob_client.return_value = mock_blob_client_instance

    main(event)

    mock_document_processor.assert_called_once()
    mock_blob_client.assert_called_once_with(container_name="test_container")
    mock_blob_client_instance.get_blob_sas.assert_called_once_with("test_file.txt")
    mock_document_processor_instance.process.assert_called_once()
    mock_blob_client_instance.upsert_blob_metadata.assert_called_once_with("test_file.txt", {'embeddings_added': 'true'})