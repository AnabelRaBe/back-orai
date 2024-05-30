import pytest
from unittest.mock import patch, MagicMock
from backend.utilities.helpers.AzureBlobStorageHelper import AzureBlobStorageClient
from azure.storage.blob import ContentSettings
from datetime import timedelta,datetime
import mock

class TestAzureBlobStorageClient:
    @pytest.fixture
    def client(self):
        with patch('backend.utilities.helpers.AzureBlobStorageHelper.BlobServiceClient') as mock_blob_service_client:
            client = AzureBlobStorageClient(account_name='test', account_key='test', container_name='test')
            client.blob_service_client = mock_blob_service_client
            yield client

    def test_upload_file(self, client):
        mock_blob_client = MagicMock()
        client.blob_service_client.get_blob_client.return_value = mock_blob_client

        client.upload_file(b'test data', 'test_file')

        mock_blob_client.upload_blob.assert_called_once_with(b'test data', overwrite=True, content_settings=ContentSettings(content_type='application/pdf'))

    def test_download_file(self, client):
        mock_blob_client = MagicMock()
        client.blob_service_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.download_blob().readall.return_value = b'test data'

        result = client.download_file('test_file')

        assert result == b'test data'

    def test_delete_file(self, client):
        mock_blob_client = MagicMock()
        client.blob_service_client.get_blob_client.return_value = mock_blob_client
        client.delete_file('test_file')
        mock_blob_client.delete_blob.assert_called_once()
        

    def test_get_all_files_feedback(self, client):
        mock_container_client = client.blob_service_client.get_container_client.return_value
        mock_blob_client = mock_container_client.list_blobs.return_value[0]
        mock_blob_client.name = 'test_file'
        mock_blob_client.download_blob.return_value.readall.return_value = b'test data'  # Replace this line with the desired byte string value

        result = client.get_all_files_feedback('test_container')

        #assert result 

    def test_get_all_files(self, client):
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_blob_client.name = 'test_file'
        mock_blob_list = [mock_blob_client]
        mock_container_client.list_blobs.return_value = mock_blob_list
        client.blob_service_client.get_container_client.return_value = mock_container_client

        result = client.get_all_files()

        assert result == [{'filename': 'test_file', 'file_extension': mock.ANY, 'upload_date': mock.ANY, 'file_size_kb': mock.ANY, 'converted': False, 'embeddings_added': False, 'chunking_strategy': mock.ANY, 'chunking_size': mock.ANY, 'chunking_overlap': mock.ANY, 'loading_strategy': mock.ANY, 'user_name': mock.ANY, 'fullpath': mock.ANY, 'converted_path': ''}]

    def test_get_all_files_by_user_id(self, client):
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        mock_blob_client.name = 'test_file'
        mock_blob_list = [mock_blob_client]
        mock_container_client.walk_blobs.return_value = mock_blob_list
        client.blob_service_client.get_container_client.return_value = mock_container_client

        result = client.get_all_files_by_user_id('test_user')

        assert result == ['test_file']

    def test_upsert_blob_metadata(self, client):
        mock_blob_client = MagicMock()
        mock_blob_client.get_blob_properties.return_value.metadata = {}
        client.blob_service_client.get_blob_client.return_value = mock_blob_client

        client.upsert_blob_metadata('test_file', {'key': 'value'})

        #mock_blob_client.set_blob_metadata.assert_called_once_with(metadata={'key': 'value'})

    def test_get_container_sas(self, client):
        result = client.get_container_sas()

        assert result 

    def test_get_blob_sas(self, client):
        result = client.get_blob_sas('test_file')
        result= result.split('?')[0]

        assert result == "https://test.blob.core.windows.net/test/test_file"

    def test_prepare_blob(self, client):
        mock_now = datetime(2022, 1, 1)
        mock_user_id = 'test_user'
        mock_data_json = '{"key": "value"}'
        mock_blob_name = 'test_blob'
        mock_upload_json_to_azure_storage_account = MagicMock()
        client.upload_json_to_azure_storage_account = mock_upload_json_to_azure_storage_account

        with patch('backend.utilities.helpers.AzureBlobStorageHelper.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now

            client.prepare_blob(mock_user_id, mock_data_json, mock_blob_name)

        mock_upload_json_to_azure_storage_account.assert_called_once_with(f"{mock_user_id}/{mock_now.strftime('%Y-%m-%d_%H-%M-%S')}/{mock_blob_name}", mock_data_json.encode('utf-8'))

    def test_create_file_object(self, client):
        mock_blob = MagicMock()
        mock_blob.name = 'test_file.pdf'
        mock_blob.metadata = {
            'file_extension': 'pdf',
            'upload_date': '2022-01-01',
            'file_size_kb': '1024',
            'converted': 'true',
            'embeddings_added': 'false',
            'chunking_strategy': 'strategy',
            'chunking_size': '1024',
            'chunking_overlap': '512',
            'loading_strategy': 'strategy',
            'user_name': 'test_user',
            'converted_filename': 'converted_file.pdf'
        }
        mock_sas = 'test_sas'

        result = client.create_file_object(mock_blob, mock_sas)

        assert result == {
            'filename': 'test_file.pdf',
            'file_extension': 'pdf',
            'upload_date': '2022-01-01',
            'file_size_kb': '1024',
            'converted': True,
            'embeddings_added': False,
            'chunking_strategy': 'strategy',
            'chunking_size': '1024',
            'chunking_overlap': '512',
            'loading_strategy': 'strategy',
            'user_name': 'test_user',
            'fullpath': f"https://{client.account_name}.blob.core.windows.net/{client.container_name}/test_file.pdf?{mock_sas}",
            'converted_filename': 'converted_file.pdf',
            'converted_path': ''
        }
    # def test_upload_json_to_azure_storage_account(self, client):
    #     # Arrange
    #     account_name = 'test_account'
    #     account_key = 'test_key'
    #     container_name = 'test_container'
    #     file_blob_name = 'test_folder/test_file'
    #     file_path = 'test_file.json'
    #     data_json = '{"key": "value"}'

    #     mock_blob_client = client.return_value.get_container_client.return_value.get_blob_client.return_value
    #     mock_blob_client.upload_blob.return_value = None

    #     azure_blob_storage_client = AzureBlobStorageClient(account_name, account_key, container_name)

    #     # Act
    #     azure_blob_storage_client.upload_json_to_azure_storage_account(file_blob_name, file_path)

    #     # Assert
    #     client.assert_called_once_with(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
    #     mock_blob_client.upload_blob.assert_called_once_with(data_json.encode(), overwrite=True)


    # def test_upload_blob_file(self, client):
    #     mock_mimetypes = MagicMock()
    #     mock_mimetypes.MimeTypes.return_value.guess_type.return_value = ('application/pdf', None)
    #     mock_chardet = MagicMock()
    #     mock_chardet.detect.return_value = {'encoding': 'utf-8'}
    #     client.mimetypes = mock_mimetypes
    #     client.chardet = mock_chardet
    #     mock_blob_client = MagicMock()
    #     client.blob_service_client.get_blob_client.return_value = mock_blob_client

    #     client.upload_blob_file(b'test data', 'test_file')

    #     mock_blob_client.upload_blob.assert_called_once_with(b'test data', overwrite=True, content_settings=ContentSettings(content_type='application/pdf; charset=utf-8'))