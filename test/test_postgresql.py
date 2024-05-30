import pytest
from unittest.mock import patch, MagicMock
from backend.utilities.common.PostgreSQL import PostgreSQL

class TestPostgreSQL:
    @pytest.fixture
    def db(self):
        with patch('backend.utilities.common.PostgreSQL.psycopg') as mock_psycopg:
            db = PostgreSQL()
            db.connection = mock_psycopg.connect.return_value
            yield db

    def test_create_table(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        db.create_table('test_table', 'id SERIAL PRIMARY KEY, name VARCHAR(255)')

        mock_cursor.execute.assert_called_once_with("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(255))")
        db.connection.commit.assert_called_once()

    def test_insert_data(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        db.insert_data('test_table', "'John Doe', 25", "(name, age)")

        mock_cursor.execute.assert_called_once_with("INSERT INTO test_table (name, age) VALUES ('John Doe', 25)")
        db.connection.commit.assert_called_once()

    def test_select_data(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('John Doe', 25), ('Jane Smith', 30)]

        result = db.select_data('test_table', "age > 20", "name, age")

        assert result == [('John Doe', 25), ('Jane Smith', 30)]
        mock_cursor.execute.assert_called_once_with("SELECT name, age FROM test_table WHERE age > 20")

    def test_update_data(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        db.update_data('test_table', "age = 30", "name = 'John Doe'")

        mock_cursor.execute.assert_called_once_with("UPDATE test_table SET age = 30 WHERE name = 'John Doe'")
        db.connection.commit.assert_called_once()

    def test_delete_data(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        db.delete_data('test_table', "age > 30")

        mock_cursor.execute.assert_called_once_with("DELETE FROM test_table WHERE age > 30")
        db.connection.commit.assert_called_once()

    def test_get_max_id_by_conversation_id(self, db):
        mock_cursor = MagicMock()
        db.connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (10,)

        result = db.get_max_id_by_conversation_id('test_table', 'conversation123')

        assert result == 10
        mock_cursor.execute.assert_called_once_with("SELECT MAX(id_message) FROM test_table WHERE conversation_id = 'conversation123'")
        mock_cursor.fetchone.assert_called_once()
    
    def test_close_connection(self, db):
        db.close_connection()

        db.connection.close.assert_called_once()