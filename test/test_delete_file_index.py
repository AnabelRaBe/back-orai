import pytest
from unittest.mock import patch, MagicMock
import json
from azure.functions import HttpRequest
from backend.DeleteFileIndex.__init__ import main, output_results, delete_files_in_index

class TestFileDeletion:
    @pytest.fixture
    def search_results(self):
        mock_results = MagicMock()
        mock_results.get_count.return_value = 2
        mock_results.__iter__.return_value = iter([
            {'id': '1', 'title': 'file1.pdf'},
            {'id': '2', 'title': 'file2.pdf'}
        ])
        return mock_results
    @pytest.fixture
    def files_names(self):
        return ['file1.pdf', 'file2.pdf']

    def test_output_results_happy_path(self, search_results, files_names):
        expected_files_to_delete = {
            'file1.pdf': ['1'],
            'file2.pdf': ['2']
        }
        actual_files_to_delete = output_results(search_results, files_names)
        assert actual_files_to_delete == expected_files_to_delete, "The output_results function should correctly map files to delete."
        
    def test_delete_files_in_index_no_files(self):
        with patch('logging.exception') as mocked_logging:
            delete_files_in_index({}, MagicMock())
            mocked_logging.assert_called_once_with("No files selected")

    @pytest.mark.asyncio
    async def test_main_authentication_failure(self):
        req = HttpRequest(
            method='POST',
            url='/delete',
            body=json.dumps({'files_names': ['file1.pdf'], 'access_token': 'invalid', 'token_id': '123'}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = MagicMock(status=401, json=MagicMock(return_value={"error": "Unauthorized"}))
            mock_post.return_value.__aenter__.return_value = mock_response
            response = await main(req)
            assert response.status_code == 401, "Should return 401 status code for authentication failure"
            assert json.loads(response.get_body()) == {"error": "Unauthorized"}, "Should return the correct error message"
