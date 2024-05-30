import pytest
from unittest.mock import patch, MagicMock
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from backend.BatchStartProcessing import (
    search_metadata_by_file_name,
    add_user_id_in_metadata_key,
    set_variables_values,
    main
)

@pytest.fixture
def mock_azure_blob_storage_client():
    return MagicMock()

@pytest.fixture
def mock_eventhub_producer_client():
    return MagicMock()

@pytest.fixture
def mock_aiohttp_client_session():
    return MagicMock()

def test_search_metadata_by_file_name():
    filename = "file1.txt"
    list_metadata = [
        {"file1.txt": {"author": "John Doe", "size": "10KB"}},
        {"file2.txt": {"author": "Jane Smith", "size": "5KB"}}
    ]
    expected_result = '{"author": "John Doe", "size": "10KB"}'
    
    result = search_metadata_by_file_name(filename, list_metadata)
    
    assert result == expected_result

def test_add_user_id_in_metadata_key():
    user_id = "user123"
    metadata_list = [
        {"file1.txt": {"author": "John Doe", "size": "10KB"}},
        {"file2.txt": {"author": "Jane Smith", "size": "5KB"}}
    ]
    expected_result = [
        {"user123/file1.txt": {"author": "John Doe", "size": "10KB"}},
        {"user123/file2.txt": {"author": "Jane Smith", "size": "5KB"}}
    ]
    
    result = add_user_id_in_metadata_key(user_id, metadata_list)
    
    assert result == expected_result

def test_set_variables_values_global_index():
    is_global_index = True
    user_id = "user123"
    metadata = [
        {"file1.txt": {"author": "John Doe", "size": "10KB"}},
        {"file2.txt": {"author": "Jane Smith", "size": "5KB"}}
    ]
    expected_result = (
        None,
        None,
        [None,None],
        metadata
    )
    
    result = set_variables_values(is_global_index, user_id, metadata)
    
    assert result == expected_result

def test_set_variables_values_local_index():
    is_global_index = False
    user_id = "user123"
    metadata = [
        {"file1.txt": {"author": "John Doe", "size": "10KB"}},
        {"file2.txt": {"author": "Jane Smith", "size": "5KB"}}
    ]
    expected_result = (
        "user123-index",
        None,
        [None],
        [
            {"user123/file1.txt": {"author": "John Doe", "size": "10KB"}},
            {"user123/file2.txt": {"author": "Jane Smith", "size": "5KB"}}
        ]
    )
    
    result = set_variables_values(is_global_index, user_id, metadata)
    
    assert result == expected_result

