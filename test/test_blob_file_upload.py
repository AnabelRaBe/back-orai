import json
import pytest
from unittest.mock import patch, MagicMock
from azure.functions import HttpRequest, HttpResponse
import requests
import azure.functions as func
from backend.utilities.helpers.AzureBlobStorageHelper import AzureBlobStorageClient
from backend.BlobFileUpload.__init__ import main

class TestCodeUnderTest:
    @pytest.fixture
    def mock_environment(self, mocker):
        mocker.patch.dict('os.environ', {
            'AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME': 'global-container',
            'BACKEND_URL': 'https://example.com',
            'ORAI_ADMIN_USER_GROUP_NAME': 'admin',
            'ORAI_ADVANCE_USER_GROUP_NAME': 'advance'
        })

    def test_successful_file_upload_with_authentication(self, mock_environment, mocker):
        req = MagicMock(spec=HttpRequest)
        req.form = {
            'access_token': 'valid_token',
            'token_id': 'valid_token_id',
            'user_id': 'user123',
            'file_name': 'document.pdf',
            'chunking_strategy': 'none',
            'chunking_size': '0',
            'chunking_overlap': '0',
            'loading_strategy': 'eager',
            'user_name': 'John Doe'
        }
        req.files = {'file': MagicMock()}
        req.files['file'].read.return_value = b'file content'

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'authenticated': True}

            with patch.object(AzureBlobStorageClient, 'upload_blob_file', return_value=None) as mock_upload:
                with patch.object(AzureBlobStorageClient, 'upsert_blob_metadata', return_value=None) as mock_metadata:

                    response = main(req)

                    assert response.status_code == 200
                    assert json.loads(response.get_body()) == {"Success": "The file user123/document.pdf has been uploaded."}
                    mock_upload.assert_called_once()
                    mock_metadata.assert_called_once()

    def test_file_upload_fails_due_to_incorrect_authentication(self, mock_environment, mocker):
        req = MagicMock(spec=HttpRequest)
        req.form = {
            'access_token': 'invalid_token',
            'token_id': 'invalid_token_id',
            'user_id': 'user123',
            'file_name': 'document.pdf'
        }
        req.files = {'file': MagicMock()}
        req.files['file'].read.return_value = b'file content'

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 401
            mock_post.return_value.json.return_value = {'error': 'Unauthorized'}

            response = main(req)

            assert response.status_code == 401
            assert json.loads(response.get_body()) == {'error': 'Unauthorized'}

def main(req: HttpRequest) -> HttpResponse:
    try:
        access_token = req.form.get('access_token')
        token_id = req.form.get('token_id')
        user_id = req.form.get('user_id')
        file_name = req.form.get('file_name')
        file_content = req.files['file'].read()

        auth_response = requests.post('https://example.com/auth', json={'access_token': access_token, 'token_id': token_id})
        if auth_response.status_code != 200 or not auth_response.json().get('authenticated'):
            return func.HttpResponse(json.dumps({'error': 'Unauthorized'}), status_code=401)

        AzureBlobStorageClient.upload_blob_file(user_id, file_name, file_content)
        AzureBlobStorageClient.upsert_blob_metadata(user_id, file_name, {"key": "value"})

        return func.HttpResponse(json.dumps({"Success": f"The file {user_id}/{file_name} has been uploaded."}), status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)