import pytest
from unittest.mock import patch, Mock
from backend.utilities.helpers.AzureFormRecognizerHelper import AzureFormRecognizerClient

class TestAzureFormRecognizerClient:            
    @pytest.fixture
    def client(self):
        with patch('backend.utilities.helpers.EnvHelper') as MockEnvHelper, \
            patch('backend.utilities.helpers.AzureFormRecognizerHelper.DocumentAnalysisClient') as MockDocumentAnalysisClient:
            
            mock_env_instance = MockEnvHelper.return_value
            mock_env_instance.AZURE_FORM_RECOGNIZER_ENDPOINT = 'https://mockendpoint.cognitiveservices.azure.com/'
            mock_env_instance.AZURE_FORM_RECOGNIZER_KEY = 'mock_key'
            
            client = AzureFormRecognizerClient()
            
            client.document_analysis_client = MockDocumentAnalysisClient
            
            yield client
    def test_table_to_html(self, client):
        table_mock = Mock()
        table_mock.row_count = 2
        table_mock.cells = [
            Mock(row_index=0, column_index=0, content="Header 1", kind="columnHeader", column_span=1, row_span=1),
            Mock(row_index=0, column_index=1, content="Header 2", kind="columnHeader", column_span=1, row_span=1),
            Mock(row_index=1, column_index=0, content="Cell 1", kind="content", column_span=1, row_span=1),
            Mock(row_index=1, column_index=1, content="Cell 2", kind="content", column_span=1, row_span=1),
        ]
        
        expected_html = (
            "<table>"
            "<tr><th>Header 1</th><th>Header 2</th></tr>"
            "<tr><td>Cell 1</td><td>Cell 2</td></tr>"
            "</table>"
        )
        
        result_html = client._table_to_html(table_mock)
        
        assert result_html == expected_html
        
    def test_get_roles(self, client):
        paragraphs = [
            Mock(spans=[Mock(offset=0, length=10)], role="title"),
            Mock(spans=[Mock(offset=11, length=20)], role="paragraph"),
            Mock(spans=[Mock(offset=32, length=10)], role=None)
        ]

        expected_roles_start = {
            0: "title",
            11: "paragraph",
            32: "paragraph"
        }
        expected_roles_end = {
            10: "title",
            31: "paragraph",
            42: "paragraph"
        }

        roles_start, roles_end = client._get_roles(paragraphs)
        assert roles_start == expected_roles_start
        assert roles_end == expected_roles_end

    def test_build_page_text(self, client):
        form_recognizer_results = Mock(content="Header 1Header 2Cell 1Cell 2")
        page = Mock(spans=[Mock(offset=0, length=23)])
        roles_start = {0: "title"}
        roles_end = {8: "title"}
        table_chars = [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        
        table_cells = [
            Mock(row_index=0, column_index=0, content="Header 1", kind="columnHeader", column_span=1, row_span=1),
            Mock(row_index=0, column_index=1, content="Header 2", kind="columnHeader", column_span=1, row_span=1),
            Mock(row_index=1, column_index=0, content="Cell 1", kind="content", column_span=1, row_span=1),
            Mock(row_index=1, column_index=1, content="Cell 2", kind="content", column_span=1, row_span=1)
        ]
        table_mock = Mock(cells=table_cells)
        table_mock.row_count = 2
        
        tables_on_page = [table_mock]

        expected_page_text = (
            "<table>"
            "<tr><th>Header 1</th><th>Header 2</th></tr>"
            "<tr><td>Cell 1</td><td>Cell 2</td></tr>"
            "</table></h1>Header 2Cell 1C "
        )

        page_text = client._build_page_text(form_recognizer_results, page, roles_start, roles_end, table_chars, tables_on_page)
        assert page_text == expected_page_text

    def test_begin_analyze_document_from_url(self, client):
        source_url = "https://example.com/test.pdf"
        mock_poller = Mock()
        mock_results = Mock()
        
        mock_page = Mock()
        mock_page.spans = [Mock(offset=0, length=41)]
        mock_page.page_number = 1

        mock_paragraph = Mock()
        mock_paragraph.spans = [Mock(offset=0, length=8)]
        mock_paragraph.role = "title"

        mock_table = Mock()
        mock_table.row_count = 2
        mock_table.column_count = 2
        mock_table.cells = [
            Mock(row_index=0, column_index=0, content="Header 1", kind="columnHeader", column_span=1, row_span=1),
            Mock(row_index=0, column_index=1, content="Header 2", kind="columnHeader", column_span=1, row_span=1),
            Mock(row_index=1, column_index=0, content="Cell 1", kind="content", column_span=1, row_span=1),
            Mock(row_index=1, column_index=1, content="Cell 2", kind="content", column_span=1, row_span=1)
        ]
        mock_table.bounding_regions = [Mock(page_number=1)]
        mock_table.spans = [Mock(offset=0, length=5), Mock(offset=6, length=4)]
        
        mock_results.pages = [mock_page]
        mock_results.paragraphs = [mock_paragraph]
        mock_results.tables = [mock_table]
        mock_results.content = "Header 1Header 2Cell 1Cell 2Some additional content" 
        
        mock_poller.result.return_value = mock_results
        client.document_analysis_client.begin_analyze_document_from_url.return_value = mock_poller

        page_map = client.begin_analyze_document_from_url(source_url)
        
        expected_page_map = [
            {
                "page_number": 0,
                "offset": 0,
                "page_text": "<table><tr><th>Header 1</th><th>Header 2</th></tr><tr><td>Cell 1</td><td>Cell 2</td></tr></table>rader 2Cell 1Cell 2Some addition "
            }
        ]
        
        assert page_map == expected_page_map