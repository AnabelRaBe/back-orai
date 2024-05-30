import unittest
from unittest.mock import patch, MagicMock
from backend.utilities.document_loading.Layout import LayoutDocumentLoading
from backend.utilities.common.SourceDocument import SourceDocument

class TestLayoutDocumentLoading(unittest.TestCase):
    def setUp(self):
        self.loader = LayoutDocumentLoading()

    @patch('backend.utilities.document_loading.Layout.AzureFormRecognizerClient')
    def test_load(self, mockazureformrecognizerclient):
        document_url = "https://example.com/document.pdf"
        metadata = {
            "global_business": "Example Business",
            "divisions_and_areas": ["Division A", "Area B"],
            "tags": ["tag1", "tag2"],
            "region": "Region",
            "country": "Country",
            "language": "English",
            "year": 2022,
            "period": "Q1",
            "importance": "High",
            "security": "Confidential",
            "origin": "Origin",
            "domain": "Domain"
        }

        expected_documents = [
            SourceDocument(
                content="Page 1 content",
                source=document_url,
                page_number=1,
                offset=0,
                global_business="Example Business",
                divisions_and_areas=["Division A", "Area B"],
                tags="tag1, tag2",
                region="Region",
                country="Country",
                language="English",
                year=2022,
                period="Q1",
                importance="High",
                security="Confidential",
                origin="Origin",
                domain="Domain"
            ),
            SourceDocument(
                content="Page 2 content",
                source=document_url,
                page_number=2,
                offset=1,
                global_business="Example Business",
                divisions_and_areas=["Division A", "Area B"],
                tags="tag1, tag2",
                region="Region",
                country="Country",
                language="English",
                year=2022,
                period="Q1",
                importance="High",
                security="Confidential",
                origin="Origin",
                domain="Domain"
            )
        ]

        # Configure the mock to return the expected value
        mock_instance = mockazureformrecognizerclient.return_value
        mock_instance.begin_analyze_document_from_url.return_value = [
            {"page_text": "Page 1 content", "page_number": 1, "offset": 0},
            {"page_text": "Page 2 content", "page_number": 2, "offset": 1}
        ]

        # Call the load method
        documents = self.loader.load(document_url, metadata)

        # Assert the result
        for doc, expected_doc in zip(documents, expected_documents):
            self.assertEqual(doc.content, expected_doc.content)
            self.assertEqual(doc.source, expected_doc.source)
            self.assertEqual(doc.page_number, expected_doc.page_number)
            self.assertEqual(doc.offset, expected_doc.offset)
            self.assertEqual(doc.global_business, expected_doc.global_business)
            self.assertEqual(doc.divisions_and_areas, expected_doc.divisions_and_areas)
            self.assertEqual(doc.tags, expected_doc.tags)
            self.assertEqual(doc.region, expected_doc.region)
            self.assertEqual(doc.country, expected_doc.country)
            self.assertEqual(doc.language, expected_doc.language)
            self.assertEqual(doc.year, expected_doc.year)
            self.assertEqual(doc.period, expected_doc.period)
            self.assertEqual(doc.importance, expected_doc.importance)
            self.assertEqual(doc.security, expected_doc.security)
            self.assertEqual(doc.origin, expected_doc.origin)
            self.assertEqual(doc.domain, expected_doc.domain)
        
        mock_instance.begin_analyze_document_from_url.assert_called_once_with(document_url, use_layout=True)

if __name__ == '__main__':
    unittest.main()
