import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest, HttpResponse
from backend.FeedbackStorage.__init__ import main

class TestFeedbackStorage:
    @pytest.fixture
    def request_test(self):
        return HttpRequest(
            method='POST',
            body=b'{"access_token": "token", "token_id": "123", "user_id": "7e74a326-1a4a-4f41-9b62-7c1793e85f48", "name": "User User", "feedback":{"type":"thumbs","score":"","text":"Correct response"},"question":"Que es Orai", "answer":"chatbot", "citations": ["x","y","z"], "conversation_id": "80292513-afa6-4e07-9397-15228241311b", "config_LLM":{"model":"gpt-4-turbo", "temperature":0.7, "max_tokens":1000, "max_followups_questions":3}, "answering_prompt": "Context"}',
            headers={'Content-Type': 'application/json'},
            url='/api/endpoint'
        )

    @pytest.fixture
    def feedback_mock(self):
        with patch('backend.FeedbackStorage.__init__.Feedback') as mock_feedback:
            yield mock_feedback

    @pytest.fixture
    def response_mock(self):
        return MagicMock()

    def test_main_success(self, request_test, feedback_mock, response_mock):
        feedback_mock.return_value.generate_json_feedback.return_value = None
        response_mock.status_code = 200
        response_mock.json.return_value = {"message": "Success"}

        with patch('backend.FeedbackStorage.__init__.requests.post', return_value=response_mock):
            result = main(request_test)

        assert isinstance(result, HttpResponse)
        assert result.status_code == 204
        
    def test_main_exception(self, request_test, feedback_mock):
        feedback_mock.return_value.generate_json_feedback.side_effect = Exception("Generate json feedback error")
        result = main(request_test)
        assert isinstance(result, HttpResponse)
        assert result.status_code == 500

    def test_main_auth_error(self, request_test, feedback_mock, response_mock):
        feedback_mock.return_value.generate_json_feedback.return_value = [[False]]
        response_mock.status_code = 401
        response_mock.json.return_value = {"error": "Authentication failed"}

        with patch('backend.FeedbackStorage.__init__.requests.post', return_value=response_mock):
            result = main(request_test)

        assert isinstance(result, HttpResponse)
        assert result.status_code == 401