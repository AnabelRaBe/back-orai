import unittest
import json
from unittest.mock import patch
from azure.functions import HttpRequest, HttpResponse
from backend.ExploreData import process_explore_data

class TestExploreData(unittest.TestCase):
    @patch('backend.ExploreData.ExploreData.get_index_metadata')
    @patch('backend.ExploreData.ExploreData.get_blob_metadata')
    @patch('backend.ExploreData.ExploreData.merge_metadata')
    @patch('backend.ExploreData.requests.post')
    def test_process_explore_data_success(self, mock_post, mock_merge_metadata, mock_blob_metadata, mock_index_metadata):
        # Mock the necessary dependencies
        mock_post.return_value.status_code = 200
        mock_index_metadata.return_value = {'index': 'metadata'}
        mock_blob_metadata.return_value = {'blob': 'metadata'}
        mock_merge_metadata.return_value = {'merged': 'metadata'}

        # Create a mock HttpRequest object
        request = HttpRequest(
            method='POST',
            body=b'{"access_token": "token", "token_id": "id"}',
            headers={'Content-Type': 'application/json'},
            url='/api/ExploreData'
        )

        # Call the function
        response = process_explore_data(request)

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        #self.assertEqual(json.loads(response.data), {'merged': 'metadata'})

    @patch('backend.ExploreData.ExploreData.get_index_metadata')
    @patch('backend.ExploreData.ExploreData.get_blob_metadata')
    @patch('backend.ExploreData.ExploreData.merge_metadata')
    @patch('backend.ExploreData.requests.post')
    def test_process_explore_data_authentication_error(self, mock_post, mock_merge_metadata, mock_blob_metadata, mock_index_metadata):
        # Mock the necessary dependencies
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {'error': 'Authentication failed'}

        # Create a mock HttpRequest object
        request = HttpRequest(
            method='POST',
            body=b'{"access_token": "token", "token_id": "id"}',
            headers={'Content-Type': 'text/plain'},
            url='/api/ExploreData'
        )

        # Call the function
        response = process_explore_data(request)

        # Assert the response
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.mimetype, 'text/plain')
        #self.assertEqual(response.get_json(), {'error': 'Authentication failed'})

    @patch('backend.ExploreData.ExploreData.get_index_metadata')
    @patch('backend.ExploreData.ExploreData.get_blob_metadata')
    @patch('backend.ExploreData.ExploreData.merge_metadata')
    @patch('backend.ExploreData.requests.post')
    def test_process_explore_data_exception(self, mock_post, mock_merge_metadata, mock_blob_metadata, mock_index_metadata):
        # Mock the necessary dependencies
        mock_post.side_effect = Exception('Something went wrong')

        # Create a mock HttpRequest object
        request = HttpRequest(
            method='POST',
            body=b'{"access_token": "token", "token_id": "id"}',
            headers={'Content-Type': 'application/json'},
            url='/api/ExploreData'
        )

        # Call the function
        response = process_explore_data(request)

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.mimetype, 'application/json')
        #self.assertEqual(response.get_json(), {'Error': 'Something went wrong'})

if __name__ == '__main__':
    unittest.main()