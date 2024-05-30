import unittest
from backend.utilities.document_loading.Strategies import get_document_loader, LoadingStrategy
from backend.utilities.document_loading.Layout import LayoutDocumentLoading
from backend.utilities.document_loading.Read import ReadDocumentLoading
from backend.utilities.document_loading.Web import WebDocumentLoading
from backend.utilities.document_loading.WordDocument import WordDocumentLoading


class TestDocumentLoader(unittest.TestCase):
    def test_layout_document_loading(self):
        loader = get_document_loader(LoadingStrategy.layout.value)
        self.assertIsInstance(loader, LayoutDocumentLoading)

    def test_read_document_loading(self):
        loader = get_document_loader(LoadingStrategy.read.value)
        self.assertIsInstance(loader, ReadDocumentLoading)

    def test_web_document_loading(self):
        loader = get_document_loader(LoadingStrategy.web.value)
        self.assertIsInstance(loader, WebDocumentLoading)

    def test_word_document_loading(self):
        loader = get_document_loader(LoadingStrategy.docx.value)
        self.assertIsInstance(loader, WordDocumentLoading)

    def test_unknown_loader_strategy(self):
        with self.assertRaises(Exception):
            get_document_loader('unknown_strategy')

if __name__ == '__main__':
    unittest.main()