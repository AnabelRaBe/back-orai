import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest, HttpResponse
from backend.CleaningConversations.__init__ import main

class TestDeleteConversation:
    @pytest.fixture
    def mock_request(self):
        return HttpRequest(
            method='POST',
            body=b'{"access_token": "dummy_token", "token_id": "dummy_token_id", "user_id": "02dcd3d7-de22-414e-bf6d-e85d9f3f4784"}',
            headers={'Content-Type': 'application/json'},
            url='/api/endpoint'
        )

    @pytest.fixture
    def postgresql_mock(self):
        with patch('backend.CleaningConversations.__init__.PostgreSQL') as mock_postgresql:
            yield mock_postgresql

    @pytest.fixture
    def response_mock(self):
        return MagicMock()
    def test_main_success(self, response_mock, postgresql_mock, mock_request):
        postgresql_mock.return_value.delete_data.return_value = None
        response_mock.status_code = 200
        response_mock.json.return_value = {"message": "Success"}

        with patch('backend.CleaningConversations.__init__.requests.post', return_value=response_mock):
            response = main(mock_request)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 204

    def test_main_auth_error(self, response_mock, postgresql_mock, mock_request):
        response_mock.status_code = 401
        response_mock.json.return_value = {"message": "Success"}

        with patch('backend.CleaningConversations.__init__.requests.post', return_value=response_mock):
            response = main(mock_request)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 401

    def test_main_exception(self, response_mock, postgresql_mock, mock_request):
        response_mock.return_value.status_code = 500
        postgresql_mock.return_value.delete_data.side_effect = Exception("Database error")

        with patch('backend.CleaningConversations.__init__.requests.post', return_value=response_mock):
         response = main(mock_request)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 500
