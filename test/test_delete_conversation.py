import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest, HttpResponse
from backend.DeleteConversation.__init__ import main

class TestDeleteConversation:
    @pytest.fixture
    def request_test(self):
        return HttpRequest(
            method='POST',
            body=b'{"access_token": "token", "token_id": "123", "conversation_id": "02dcd3d7-de22-414e-bf6d-e85d9f3f4784", "delete": true}',
            headers={'Content-Type': 'application/json'},
            url='/api/endpoint'
        )

    @pytest.fixture
    def postgresql_mock(self):
        with patch('backend.DeleteConversation.__init__.PostgreSQL') as mock_postgresql:
            yield mock_postgresql

    @pytest.fixture
    def response_mock(self):
        return MagicMock()

    def test_main_success(self, request_test, postgresql_mock, response_mock):
        postgresql_mock.return_value.select_data.return_value = [[True]]
        postgresql_mock.return_value.delete_data.return_value = None
        postgresql_mock.return_value.close_connection.return_value = None
        response_mock.status_code = 200
        response_mock.json.return_value = {"message": "Success"}

        with patch('backend.DeleteConversation.__init__.requests.post', return_value=response_mock):
            result = main(request_test)

        assert isinstance(result, HttpResponse)
        assert result.status_code == 204

    def test_main_auth_error(self, request_test, postgresql_mock, response_mock):
        postgresql_mock.return_value.select_data.return_value = [[False]]
        response_mock.status_code = 401
        response_mock.json.return_value = {"error": "Authentication failed"}

        with patch('backend.DeleteConversation.__init__.requests.post', return_value=response_mock):
            result = main(request_test)

        assert isinstance(result, HttpResponse)
        assert result.status_code == 401

    def test_main_exception(self, request_test, postgresql_mock):
        postgresql_mock.return_value.select_data.side_effect = Exception("Database error")

        result = main(request_test)

        assert isinstance(result, HttpResponse)
        assert result.status_code == 500