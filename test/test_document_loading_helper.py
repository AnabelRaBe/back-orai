import pytest
from backend.utilities.helpers.DocumentLoadingHelper import DocumentLoading, LoadingSettings
from unittest.mock import patch, Mock

class TestDocumentLoading:
    def test_init(self):
        document_loading = DocumentLoading()
        assert document_loading is not None

    @patch('backend.utilities.helpers.DocumentLoadingHelper.get_document_loader')
    def test_load(self, mock_get_document_loader):
        mock_loader = Mock()
        mock_get_document_loader.return_value = mock_loader
        mock_loader.load.return_value = ['document1', 'document2']

        document_loading = DocumentLoading()
        loading_settings = LoadingSettings({'strategy': 'docx'})
        documents = document_loading.load('document_url', loading_settings, {})

        mock_get_document_loader.assert_called_once_with(loader_strategy='docx')
        mock_loader.load.assert_called_once_with(document_url='document_url', metadata={})
        assert documents == ['document1', 'document2']