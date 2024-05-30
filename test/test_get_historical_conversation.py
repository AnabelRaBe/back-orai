import pytest
import datetime
from unittest import mock
from backend.GetHistoricalConversation import main

class TestGetHistoricalConversation:
    @mock.patch('requests.post')
    @mock.patch('backend.GetHistoricalConversation.PostgreSQL')
    def test_main_success(self, mock_postgresql, mock_post):
        # Mocking the request
        request_body = {
            "conversation_id": "12345",
            "access_token": "token",
            "token_id": "token_id"
        }
        mock_request = mock.Mock()
        mock_request.get_json.return_value = request_body

        # Mocking the response from the backend authentication API
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # Mocking the messages retrieved from the database
        mock_messages = [
            (1, {"author": "John", "content": "Hello"}, datetime.datetime(2022, 1, 1)),
            (2, {"author": "Jane", "content": "Hi"}, datetime.datetime(2022, 1, 2))
        ]
        mock_postgresql.return_value.select_data.return_value = mock_messages

        # Calling the main function
        response = main(mock_request)

        # Assertions
        assert response.status_code == 200
        
    @mock.patch('requests.post')
    def test_main_authentication_error(self, mock_post):
        # Mocking the request
        request_body = {
            "conversation_id": "12345",
            "access_token": "token",
            "token_id": "token_id"
        }
        mock_request = mock.Mock()
        mock_request.get_json.return_value = request_body

        # Mocking the response from the backend authentication API
        mock_response = mock.Mock()
        mock_response.status_code = 401

    @mock.patch('requests.post')
    def test_main_exception(self, mock_post):
        # Mocking the request
        request_body = {
            "conversation_id": "12345",
            "access_token": "token",
            "token_id": "token_id"
        }
        mock_request = mock.Mock()
        mock_request.get_json.return_value = request_body

        # Mocking the response from the backend authentication API
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # Mocking the exception in PostgreSQL select_data
        mock_postgresql = mock.Mock()
        mock_postgresql.select_data.side_effect = Exception("Database error")
        mock_postgresql.return_value = mock_postgresql

        # Calling the main function
        response = main(mock_request)

        # Assertions
        assert response.status_code == 500
        