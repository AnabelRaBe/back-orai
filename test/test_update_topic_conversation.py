import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest, HttpResponse
from backend.UpdateTopicConversation import main

class TestUpdateTopicConversation:
    @patch('backend.UpdateTopicConversation.PostgreSQL')
    @patch('backend.UpdateTopicConversation.requests')
    @patch('backend.UpdateTopicConversation.datetime')
    @patch('backend.UpdateTopicConversation.load_dotenv')
    def test_main_success(self, mock_load_dotenv, mock_datetime, mock_requests, mock_postgresql):
        # Mocking the necessary dependencies
        mock_req = MagicMock(spec=HttpRequest)
        mock_postgresql_instance = MagicMock()
        mock_postgresql.return_value = mock_postgresql_instance
        mock_datetime_instance = MagicMock()
        mock_datetime.now.return_value = mock_datetime_instance
        mock_datetime_instance.isoformat.return_value = '2022-01-01T00:00:00'
        mock_response = MagicMock(spec=HttpResponse)
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        # Setting up the request body
        request_body = {
            "access_token": "access_token",
            "token_id": "token_id",
            "topic": "new_topic",
            "conversation_id": "conversation123",
            "user_id": "user123"
        }
        mock_req.get_json.return_value = request_body

        # Calling the main function
        result = main(mock_req)

        # Assertions
        mock_load_dotenv.assert_called_once()
        mock_req.get_json.assert_called_once()

    @patch('backend.UpdateTopicConversation.PostgreSQL')
    @patch('backend.UpdateTopicConversation.requests')
    @patch('backend.UpdateTopicConversation.load_dotenv')
    def test_main_authentication_error(self, mock_load_dotenv, mock_requests, mock_postgresql):
        # Mocking the necessary dependencies
        mock_req = MagicMock(spec=HttpRequest)
        mock_postgresql_instance = MagicMock()
        mock_postgresql.return_value = mock_postgresql_instance
        mock_response = MagicMock(spec=HttpResponse)
        mock_response.status_code = 401
        mock_requests.post.return_value = mock_response

        # Setting up the request body
        request_body = {
            "access_token": "access_token",
            "token_id": "token_id",
            "topic": "new_topic",
            "conversation_id": "conversation123",
            "user_id": "user123"
        }
        mock_req.get_json.return_value = request_body

        # Calling the main function
        result = main(mock_req)

        # Assertions
        mock_load_dotenv.assert_called_once()
        mock_req.get_json.assert_called_once()
        mock_postgresql.assert_not_called()
        mock_postgresql_instance.update_data.assert_not_called()
        mock_postgresql_instance.close_connection.assert_not_called()

    @patch('backend.UpdateTopicConversation.PostgreSQL')
    @patch('backend.UpdateTopicConversation.load_dotenv')
    def test_main_exception(self, mock_load_dotenv, mock_postgresql):
        # Mocking the necessary dependencies
        mock_req = MagicMock(spec=HttpRequest)
        mock_postgresql_instance = MagicMock()
        mock_postgresql.return_value = mock_postgresql_instance
        mock_postgresql_instance.update_data.side_effect = Exception("Database error")

        # Setting up the request body
        request_body = {
            "access_token": "access_token",
            "token_id": "token_id",
            "topic": "new_topic",
            "conversation_id": "conversation123",
            "user_id": "user123"
        }
        mock_req.get_json.return_value = request_body

        # Calling the main function
        result = main(mock_req)

        # Assertions
        mock_load_dotenv.assert_called_once()
        mock_req.get_json.assert_called_once()
        assert result.status_code == 500