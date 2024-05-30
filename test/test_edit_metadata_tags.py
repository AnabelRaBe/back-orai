import json
import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest
from backend.EditMetadataTags.__init__ import main

@pytest.fixture
def mock_env_variables():
    with patch('backend.EditMetadataTags.os.getenv') as mock_getenv:
        def getenv_side_effect(key):
            if key == "ORAI_ADMIN_USER_GROUP_NAME":
                return "admin_group"
            elif key == "ORAI_ADVANCE_USER_GROUP_NAME":
                return "advance_group"
            elif key == "BACKEND_URL":
                return "https://example.com"
            return None

        mock_getenv.side_effect = getenv_side_effect
        yield mock_getenv

@pytest.fixture
def mock_requests_post():
    with patch('backend.EditMetadataTags.requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mock_edit_tags_options_as_active():
    with patch('backend.EditMetadataTags.ConfigHelper.edit_tags_options_as_active') as mock_edit:
        yield mock_edit

def test_main_success(mock_env_variables, mock_requests_post, mock_edit_tags_options_as_active):
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.get_json.return_value = {
        "access_token": "access_token",
        "token_id": "token_id",
        "tags": ["tag1", "tag2"]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests_post.return_value = mock_response

    result = main(mock_request)

    assert result.status_code == 200
    assert json.loads(result.get_body().decode()) == {"Success": "New tags saved successfully!"}

    mock_edit_tags_options_as_active.assert_called_once_with(["tag1", "tag2"])

def test_main_backend_request_failed(mock_env_variables, mock_requests_post, mock_edit_tags_options_as_active):
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.get_json.return_value = {
        "access_token": "access_token",
        "token_id": "token_id",
        "tags": ["tag1", "tag2"]
    }

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_requests_post.return_value = mock_response

    main(mock_request)

    mock_edit_tags_options_as_active.assert_not_called()

def test_main_failed_to_edit_tags(mock_env_variables, mock_requests_post, mock_edit_tags_options_as_active):
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.get_json.return_value = {
        "access_token": "access_token",
        "token_id": "token_id",
        "tags": ["tag1", "tag2"]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests_post.return_value = mock_response

    mock_edit_tags_options_as_active.side_effect = Exception("Failed to edit tags")

    result = main(mock_request)

    assert result.status_code == 500
    assert json.loads(result.get_body().decode()) == {"error": "Failed to edit tags"}

def test_main_exception_handling(mock_env_variables, mock_requests_post, mock_edit_tags_options_as_active):
    mock_request = MagicMock(spec=HttpRequest)
    mock_request.get_json.return_value = {
        "access_token": "access_token",
        "token_id": "token_id",
        "tags": ["tag1", "tag2"]
    }

    mock_requests_post.side_effect = Exception("Failed to connect to backend")

    result = main(mock_request)

    assert result.status_code == 500
    assert json.loads(result.get_body().decode()) == {"Error": "Failed to connect to backend"}
