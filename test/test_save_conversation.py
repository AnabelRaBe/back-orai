import pytest
from unittest.mock import patch, MagicMock
from backend.utilities.common.PostgreSQL import PostgreSQL
from backend.SaveConversation import set_user, set_message, set_topic, main

class TestSaveConversation:
    @pytest.fixture
    def db(self):
        with patch('backend.utilities.common.PostgreSQL.psycopg') as mock_psycopg:
            db = PostgreSQL()
            db.connection = mock_psycopg.connect.return_value
            yield db

    def test_set_user(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor
        request_body = MagicMock()
        request_body.user_id = 'user123'
        request_body.user_name = 'John Doe'
        timestamptz = '2022-01-01T00:00:00'
        rows = []
        
        set_user(rows, db, request_body, timestamptz)
        db.connection.commit.assert_called_once()

        # db.select_data.assert_called_once()
        # db.insert_data.assert_called_once_with("users", "'user123', 'John Doe', '2022-01-01T00:00:00'", "(user_id, username, created_at)")
        # db.insert_data.assert_called_once_with("conversations", "'conversation123', 'user123', 'save_chat', 'language', '2022-01-01T00:00:00', '2022-01-01T00:00:00'", "(conversation_id, user_id, save_chat, language, created_at, modified_at)")
        # assert result == db



    def test_set_message(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor
        request_body = MagicMock()
        mock_get_max = MagicMock()
        request_body.message = ['Hello', 'World']
        request_body.conversation_id = 'conversation123'
        request_body.user_id = 'user123'
        timestamptz = '2022-01-01T00:00:00'
        mock_get_max.get_max_id_by_conversation_id.return_value = 5
        
        set_message(request_body, db, timestamptz)
        db.connection.commit.assert_called()

    @patch('backend.SaveConversation.GenerateTopicTool.generate_topic')
    def test_set_topic(self, mock_generate_topic_tool, db):
        request_body = MagicMock()
        request_body.save_chat = True
        request_body.conversation_id = 'conversation123'
        request_body.user_id = 'user123'
        rows = [(True, 'en', None)]
        timestamptz = '2022-01-01T00:00:00'
        mock_generate_topic_tool.return_value = 'generated_topic'
        
        result = set_topic(request_body, rows, db, timestamptz)
        assert result == db

