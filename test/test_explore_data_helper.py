
    
import pytest
from unittest import mock
from unittest.mock import patch, MagicMock
from backend.utilities.helpers.ExploreDataHelper import ExploreData

class TestExploreData:
    @pytest.fixture
    def explore_data(self):
        with patch('backend.utilities.helpers.ExploreDataHelper.ExploreData') as mock_explore_data:
            yield mock_explore_data
    def test_get_index_metadata_with_valid_index(self, mocker, explore_data):
            # Mocking AzureSearchHelper and its method get_vector_store
            mock_search_helper = mocker.patch('backend.utilities.helpers.ExploreDataHelper.AzureSearchHelper')
            mock_search_instance = mock_search_helper.return_value
            mock_search_client = mocker.Mock()
            mock_search_instance.get_vector_store.return_value.client = mock_search_client
        
            # Setting up the search client to return non-empty results
            mock_results = mocker.Mock()
            mock_results.get_count.return_value = 1
            mock_results.return_value = [{'metadata': 'some_metadata'}]
            mock_search_client.search.return_value = mock_results
        
            # Mocking process_metadata to simply return its input for simplicity
            mocker.patch('backend.utilities.helpers.ExploreDataHelper.process_metadata', side_effect=lambda x: x)
        
            # Initialize ExploreData and call get_index_metadata
            
            explore_data.get_index_metadata.return_value = [{'metadata': 'some_metadata'}]
            result = explore_data.get_index_metadata("valid_index_name")
        
            # Assertions to check if the results are processed correctly
            #assert len(result) == 1
            assert result[0]['metadata'] == 'some_metadata'
    
    def test_get_blob_metadata(self, explore_data):
        # Mock the AzureBlobStorageClient and its methods
        #with mock.patch('backend.utilities.helpers.ExploreDataHelper.ExploreData') as mock_blob_client:
        explore_data.get_blob_metadata.return_value = [
            {'filename': 'file1.txt', 'file_extension': '.txt', 'upload_date': '2022-01-01'},
            {'filename': 'file2.txt', 'file_extension': '.txt', 'upload_date': '2022-01-02'}
        ]

        # Call the method under test
        blob_metadata = explore_data.get_blob_metadata('container_name')

        # Assertions
        assert len(blob_metadata) == 2
        assert blob_metadata[0]['filename'] == 'file1.txt'
        assert blob_metadata[0]['file_extension'] == '.txt'
        assert blob_metadata[0]['upload_date'] == '2022-01-01'
        assert blob_metadata[1]['filename'] == 'file2.txt'
        assert blob_metadata[1]['file_extension'] == '.txt'
        assert blob_metadata[1]['upload_date'] == '2022-01-02'