import pytest
from unittest.mock import patch
from azure.functions import HttpRequest
from backend.ConversationOrquestrator import main

class TestConversationOrquestrator:

    @pytest.fixture
    def request_test(self):
        return HttpRequest(
            method='POST',
            body=b'''{
                    "chat_history": {
                        "messages": [
                            {
                            "role": "user", 
                            "content": "Hello"
                            }
                        ],
                        "conversation_id": "123456"
                    },
                    "language": "en",
                    "user_index_name": "user123",
                    "access_token": "test_access_token",
                    "token_id": "test_token_id"}''',
                
            headers={'Content-Type': 'application/json'},
            url='/api/endpoint'
        )
    @patch('backend.ConversationOrquestrator.requests.post')
    @patch('backend.utilities.helpers.OrchestratorHelper.Orchestrator.handle_message')
    def test_main_successful_response(self, mock_handle_message, mock_post, request_test):
        # Mock the response from the backend authentication endpoint
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "test_token", "token_id": "test_token_id"}
        mock_handle_message.return_value = [{'role': 'tool', 'content': '{"citations": [], "intent": "Hello"}', 'end_turn': False}, {'role': 'assistant', 'content': 'Hi, how can I help you.', 'end_turn': True}]
        response = main(request_test)

        # Assert that the response is valid
        assert response.status_code == 200
    
    @patch('backend.ConversationOrquestrator.requests.post')
    @patch('backend.utilities.helpers.OrchestratorHelper.Orchestrator.handle_message')
    def test_main_auth_error(self, mock_handle_message, mock_post, request_test):
        # Mock the response from the backend authentication endpoint
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"access_token": "test_token", "token_id": "test_token_id"}
        mock_handle_message.return_value = [{'role': 'tool', 'content': '{"citations": [], "intent": "Hello"}', 'end_turn': False}, {'role': 'assistant', 'content': 'Hi, how can I help you.', 'end_turn': True}]
        response = main(request_test)

        # Assert that the response is valid
        assert response.status_code == 401