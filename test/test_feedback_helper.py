import pytest
import json
from datetime import datetime
from backend.utilities.helpers.FeedbackHelper import Feedback

class TestFeedbackHelper:
    # def test_init(self):
    #     feedback_helper = Feedback('conversation_id', 'feedback', 'question', 'prompt', 'answer', 'citations', 'config_LLM', 'user_id', 'blob_storage_client')
    #     assert feedback_helper.conversation_id == 'conversation_id'
    #     assert feedback_helper.feedback == 'feedback'
    #     assert feedback_helper.question == 'question'
    #     assert feedback_helper.prompt == 'prompt'
    #     assert feedback_helper.answer == 'answer'
    #     assert feedback_helper.citations == 'citations'
    #     assert feedback_helper.config_LLM == 'config_LLM'
    #     assert feedback_helper.user_id == 'user_id'
    #     assert feedback_helper.blob_storage_client == 'blob_storage_client'

    def test_prepare_blob(self, mocker):
        feedback_helper = Feedback('conversation_id', 'feedback', 'question', 'prompt', 'answer', 'citations', 'config_LLM', 'user_id', 'blob_storage_client')
        mocker.patch.object(feedback_helper.blob_storage_client, 'prepare_blob')
        feedback_helper.blob_storage_client.prepare_blob('user_id', 'data_json', 'blob_name')
        feedback_helper.blob_storage_client.prepare_blob.assert_called_once_with('user_id', 'data_json', 'blob_name')