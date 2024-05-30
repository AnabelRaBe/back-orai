import pytest
from backend.utilities.document_loading.DocumentLoadingBase import DocumentLoadingBase
from backend.utilities.common.SourceDocument import SourceDocument

class MockDocumentLoader(DocumentLoadingBase):
    def load(self, document_url: str, metadata: dict):
        return [SourceDocument("content", "source")]

def test_load_method():
    loader = MockDocumentLoader()
    result = loader.load("http://example.com", {})
    assert isinstance(result, list)
    assert all(isinstance(doc, SourceDocument) for doc in result)
    assert result[0].content == "content"
    assert result[0].source == "source"

def test_base_class_instantiation():
    with pytest.raises(TypeError):
        _ = DocumentLoadingBase()