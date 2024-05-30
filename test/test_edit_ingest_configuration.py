import json
import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest
from backend.EditIngestConfiguration.__init__ import main

@pytest.fixture
def mock_env_variables():
    with patch('backend.EditIngestConfiguration.os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "ORAI_ADMIN_USER_GROUP_NAME": "admin_group",
            "ORAI_ADVANCE_USER_GROUP_NAME": "advance_group",
            "BACKEND_URL": "https://example.com"
        }.get(key)

        yield mock_getenv

@pytest.fixture
def mock_requests_post():
    with patch('backend.EditIngestConfiguration.requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mock_edit_ingest_config_as_active():
    with patch('backend.EditIngestConfiguration.ConfigHelper.edit_ingest_config_as_active') as mock_edit:
        yield mock_edit

def test_main_success(mock_env_variables, mock_requests_post, mock_edit_ingest_config_as_active):
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.get_json.return_value = {
        "access_token": "access_token",
        "token_id": "token_id",
        "document_processors": ["processor1", "processor2"]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests_post.return_value = mock_response

    result = main(mock_request)

    assert result.status_code == 200
    assert json.loads(result.get_body().decode()) == {"Success": "Configuration saved successfully!"}

    mock_edit_ingest_config_as_active.assert_called_once_with(["processor1", "processor2"])

def test_main_backend_failure(mock_env_variables, mock_requests_post, mock_edit_ingest_config_as_active):
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.get_json.return_value = {
        "access_token": "access_token",
        "token_id": "token_id",
        "document_processors": ["processor1", "processor2"]
    }

    mock_response = MagicMock()
    mock_response.status_code = 401  # Unauthorized
    mock_requests_post.return_value = mock_response

    main(mock_request)

    mock_edit_ingest_config_as_active.assert_not_called()