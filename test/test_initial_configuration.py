import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest, HttpResponse
from backend.InitialConfiguration import main

@pytest.fixture
def mock_requests_post():
    with patch('backend.InitialConfiguration.requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mock_azure_blob_storage_client():
    with patch('backend.InitialConfiguration.AzureBlobStorageClient') as mock_client:
        yield mock_client

def test_main_success(mock_requests_post, mock_azure_blob_storage_client):
    mock_requests_post.return_value.status_code = 200
    mock_requests_post.return_value.json.return_value = {}

    mock_blob_client = MagicMock()
    mock_blob_client.download_file.return_value = '{"key": "value"}'
    mock_azure_blob_storage_client.return_value = mock_blob_client

    req = HttpRequest(method='POST', body='{"access_token": "token", "token_id": "123"}'.encode("utf-8"), url='/api/InitialConfiguration')

    response = main(req)

    assert response.status_code == 200
    assert response.get_body() == b'{"key": "value"}'
    mock_requests_post.assert_called_once()
    mock_blob_client.download_file.assert_called_once_with('active.json')

def test_main_authentication_error(mock_requests_post):
    mock_requests_post.return_value.status_code = 401
    mock_requests_post.return_value.json.return_value = {'error': 'Authentication failed'}

    req = HttpRequest(method='POST', body='{"access_token": "token", "token_id": "123"}'.encode("utf-8"), url='/api/InitialConfiguration')

    response = main(req)

    assert response.status_code == 401
    assert response.get_body() == b'{"error": "Authentication failed"}'
    mock_requests_post.assert_called_once()

def test_main_exception(mock_requests_post, mock_azure_blob_storage_client):
    mock_requests_post.side_effect = Exception('Some error')

    req = HttpRequest(method='POST', body='{"access_token": "token", "token_id": "123"}'.encode("utf-8"), url='/api/InitialConfiguration')

    response = main(req)

    assert response.status_code == 500
    assert response.get_body() == b'{"Error": "Some error"}'
    mock_requests_post.assert_called_once()