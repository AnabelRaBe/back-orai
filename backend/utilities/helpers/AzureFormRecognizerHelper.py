"""
This module provides a client class for interacting with the Azure Form Recognizer service.
It includes methods for converting tables to HTML, analyzing documents from URLs, and building page maps.
"""
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import html
import traceback
from .EnvHelper import EnvHelper

class AzureFormRecognizerClient:
    """
    A client class for interacting with Azure Form Recognizer service.
    Attributes:
        AZURE_FORM_RECOGNIZER_ENDPOINT (str): The endpoint URL of the Azure Form Recognizer service.
        AZURE_FORM_RECOGNIZER_KEY (str): The API key for accessing the Azure Form Recognizer service.
        document_analysis_client (DocumentAnalysisClient): The client object for performing document analysis.
    Methods:
        _table_to_html(table): Converts a table object to an HTML representation.
        begin_analyze_document_from_url(source_url, use_layout=True, paragraph_separator=""): Analyzes a document from a URL and returns the page map.
    """
    def __init__(self) -> None:
        """
        Initializes an instance of AzureFormRecognizerClient.
        It retrieves the Azure Form Recognizer endpoint and key from the environment variables.
        """
        env_helper : EnvHelper = EnvHelper()
        
        self.AZURE_FORM_RECOGNIZER_ENDPOINT : str = env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT
        self.AZURE_FORM_RECOGNIZER_KEY : str = env_helper.AZURE_FORM_RECOGNIZER_KEY
        
        self.document_analysis_client = DocumentAnalysisClient(
            endpoint=self.AZURE_FORM_RECOGNIZER_ENDPOINT, credential=AzureKeyCredential(self.AZURE_FORM_RECOGNIZER_KEY)
        )
    
    form_recognizer_role_to_html = {
        "title": "h1",
        "sectionHeading": "h2",
        "pageHeader": None,
        "pageFooter": None,
        "paragraph": "p",
    }

    def _table_to_html(self, table):
        """
        Converts a table object to an HTML representation.
        Args:
            table: The table object to be converted.
        Returns:
            str: The HTML representation of the table.
        """
        table_html = "<table>"
        rows = [sorted([cell for cell in table.cells if cell.row_index == i], key=lambda cell: cell.column_index) for i in range(table.row_count)]
        for row_cells in rows:
            table_html += "<tr>"
            for cell in row_cells:
                tag = "th" if (cell.kind == "columnHeader" or cell.kind == "rowHeader") else "td"
                cell_spans = ""
                if cell.column_span > 1: cell_spans += f" colSpan={cell.column_span}"
                if cell.row_span > 1: cell_spans += f" rowSpan={cell.row_span}"
                table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
            table_html +="</tr>"
        table_html += "</table>"
        return table_html

    def begin_analyze_document_from_url(self, source_url: str, use_layout: bool = True): 
        """
        Analyzes a document from a URL and returns the page map.
        Args:
            source_url (str): The URL of the document to be analyzed.
            use_layout (bool, optional): Whether to use layout analysis or read analysis. Defaults to True.
        Returns:
            list: A list of dictionaries representing each page in the document. Each dictionary contains the page number, offset, and page text.
        Raises:
            ValueError: If an error occurs during the document analysis.
        """
        offset = 0
        page_map = []
        model_id = "prebuilt-layout" if use_layout else "prebuilt-read"

        try:
            poller = self.document_analysis_client.begin_analyze_document_from_url(model_id, document_url=source_url)
            form_recognizer_results = poller.result()

            roles_start, roles_end = self._get_roles(form_recognizer_results.paragraphs)
            
            for page_num, page in enumerate(form_recognizer_results.pages):
                tables_on_page = [table for table in form_recognizer_results.tables if table.bounding_regions[0].page_number == page_num + 1]
                
                table_chars = self._get_table_chars(tables_on_page, page)
                page_text = self._build_page_text(form_recognizer_results, page, roles_start, roles_end, table_chars, tables_on_page)

                page_map.append({"page_number": page_num, "offset": offset, "page_text": page_text})
                offset += len(page_text)
                
            return page_map
        except Exception:
            raise ValueError(f"Error: {traceback.format_exc()}")

    def _get_roles(self, paragraphs):
        """
        Extracts the roles (e.g., title, sectionHeading, paragraph) and their corresponding start and end positions from the paragraphs.
        Args:
            paragraphs: The list of paragraph objects.
        Returns:
            tuple: Two dictionaries representing the start and end positions of each role.
        """
        roles_start = {}
        roles_end = {}
        for paragraph in paragraphs:
            para_start = paragraph.spans[0].offset
            para_end = paragraph.spans[0].offset + paragraph.spans[0].length
            roles_start[para_start] = paragraph.role if paragraph.role is not None else "paragraph"
            roles_end[para_end] = paragraph.role if paragraph.role is not None else "paragraph"
        return roles_start, roles_end

    def _get_table_chars(self, tables_on_page, page):
        """
        Generates a list of table IDs for each character position on the page.
        Args:
            tables_on_page: The list of table objects on the page.
            page_offset: The offset of the page.
            page_length: The length of the page.
        Returns:
            list: A list of table IDs for each character position on the page.
        """
        page_offset = page.spans[0].offset
        page_length = page.spans[0].length
        table_chars = [-1]*page_length
        for table_id, table in enumerate(tables_on_page):
            for span in table.spans:
                for i in range(span.length):
                    idx = span.offset - page_offset + i
                    if idx >=0 and idx < page_length:
                        table_chars[idx] = table_id
        return table_chars

    def _build_page_text(self, form_recognizer_results, page, roles_start, roles_end, table_chars, tables_on_page):
        """
        Builds the text representation of a page by combining the recognized content, roles, and tables.
        Args:
            form_recognizer_results: The results of the form recognizer analysis.
            page_offset: The offset of the page.
            roles_start: The start positions of the roles.
            roles_end: The end positions of the roles.
            table_chars: The list of table IDs for each character position on the page.
            tables_on_page: The list of table objects on the page.
        Returns:
            str: The text representation of the page.
        """        
        page_offset = page.spans[0].offset
        page_text = ""
        added_tables = set()
        for idx, table_id in enumerate(table_chars):
            if table_id == -1:
                position = page_offset + idx
                page_text += self._add_html_tags(roles_start, roles_end, position)  
                page_text += form_recognizer_results.content[page_offset + idx]      
            elif table_id not in added_tables:
                page_text += self._table_to_html(tables_on_page[table_id])
                added_tables.add(table_id)
        page_text += " "
        return page_text
    
    def _add_html_tags(self, roles_start, roles_end, position):
        """
        Adds HTML tags to the text based on the roles and positions.
        Args:
            roles_start: The start positions of the roles.
            roles_end: The end positions of the roles.
            position: The current position in the text.
        Returns:
            str: The HTML tags to be added.
        """
        page_text = ""
        if position in roles_start.keys():
            role = roles_start[position]
            html_role = self.form_recognizer_role_to_html.get(role)
            if html_role is not None:
                page_text += f"<{html_role}>"
        if position in roles_end.keys():
            role = roles_end[position]
            html_role = self.form_recognizer_role_to_html.get(role)
            if html_role is not None:
                page_text += f"</{html_role}>"
        return page_text
