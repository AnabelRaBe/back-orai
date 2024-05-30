import pytest
from unittest.mock import patch, MagicMock, Mock
from langchain.docstore.document import Document
from backend.utilities.helpers.DocumentChunkingHelper import DocumentChunking, ChunkingSettings

@pytest.fixture
def mock_document():
    return Document(page_content="Sample content")

@pytest.fixture
def chunking_settings():
    return ChunkingSettings({
        'strategy': 'layout',
        'size': 100,
        'overlap': 10
    })

def test_chunk_method_returns_list_of_documents_correctly(mocker, mock_document, chunking_settings):
    mock_chunker = Mock()
    mock_chunker.chunk.return_value = [mock_document]

    mocker.patch('backend.utilities.helpers.DocumentChunkingHelper.get_document_chunker', return_value=mock_chunker)
    
    document_chunking = DocumentChunking()
    result = document_chunking.chunk([mock_document], chunking_settings)

    assert result == [mock_document]
    mock_chunker.chunk.assert_called_once_with([mock_document], chunking_settings)
    
def test_chunk_method_returns_empty_list_with_empty_documents_list(mocker, chunking_settings):
    mock_chunker = Mock()
    mock_chunker.chunk.return_value = []

    mocker.patch('backend.utilities.helpers.DocumentChunkingHelper.get_document_chunker', return_value=mock_chunker)
    
    document_chunking = DocumentChunking()
    result = document_chunking.chunk([], chunking_settings)

    assert result == []
    mock_chunker.chunk.assert_called_once_with([], chunking_settings)
