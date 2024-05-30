import pytest
from unittest.mock import patch
from backend.utilities.loggers.ConversationLogger import ConversationLogger

class TestConversationLogger:

    @patch('backend.utilities.loggers.ConversationLogger.AzureSearchHelper')
    def test_log_user_message(self, mock_azure_search_helper):
        logger = ConversationLogger()
        messages = [
            {'role': 'user', 'content': 'Hello', 'conversation_id': '123'},
            {'role': 'assistant', 'content': 'Hi there'},
            {'role': 'tool', 'content': '{"citations": [{"id": "1"}, {"id": "2"}]}'}
        ]
        logger.log_user_message(messages)
        mock_azure_search_helper.return_value.get_conversation_logger.return_value.add_texts.assert_called_once_with(
            texts=['Hello'],
            metadatas=[{
                'type': 'user',
                'conversation_id': '123',
                'created_at': mock_azure_search_helper.return_value.get_conversation_logger.return_value.add_texts.call_args[1]['metadatas'][0]['created_at'],
                'updated_at': mock_azure_search_helper.return_value.get_conversation_logger.return_value.add_texts.call_args[1]['metadatas'][0]['updated_at']
            }]
        )

    @patch('backend.utilities.loggers.ConversationLogger.AzureSearchHelper')
    def test_log_assistant_message(self, mock_azure_search_helper):
        logger = ConversationLogger()
        messages = [
            {'role': 'user', 'content': 'Hello', 'conversation_id': '123'},
            {'role': 'assistant', 'content': 'Hi there'},
            {'role': 'tool', 'content': '{"citations": [{"id": "1"}, {"id": "2"}]}'}
        ]
        logger.log_assistant_message(messages)
        mock_azure_search_helper.return_value.get_conversation_logger.return_value.add_texts.assert_called_once_with(
            texts=['Hi there'],
            metadatas=[{
                'type': 'assistant',
                'conversation_id': '123',
                'created_at': mock_azure_search_helper.return_value.get_conversation_logger.return_value.add_texts.call_args[1]['metadatas'][0]['created_at'],
                'updated_at': mock_azure_search_helper.return_value.get_conversation_logger.return_value.add_texts.call_args[1]['metadatas'][0]['updated_at'],
                'sources': ['1', '2']
            }]
        )