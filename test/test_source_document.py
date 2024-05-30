import pytest
from unittest.mock import patch
from backend.utilities.common.SourceDocument import SourceDocument

class TestSourceDocument:

    def test_initialize_with_all_parameters(self):
        # Create a SourceDocument object with all parameters
        source_doc = SourceDocument(
            content="Full content example",
            source="https://example.com/full_document.pdf",
            id="full12345",
            title="Full Sample Document",
            chunk=1,
            offset=0,
            page_number=1,
            container_name="full_documents",
            global_business="Full Global Business",
            divisions_and_areas="Full Division A",
            tags=["full_tag1", "full_tag2"],
            region="Full Region A",
            country="Full Country X",
            language="English",
            year="2022",
            period="Q1",
            importance="High",
            security="Confidential",
            origin="Origin Full",
            domain="Domain Full"
        )
        # Assert that the object is correctly initialized
        assert source_doc.id == "full12345"
        assert source_doc.title == "Full Sample Document"
        assert source_doc.tags == ["full_tag1", "full_tag2"]
        assert source_doc.language == "English"

    def test_initialize_with_minimal_parameters(self):
        # Create a SourceDocument object with minimal parameters
        source_doc = SourceDocument(
            content="Minimal content example",
            source="https://example.com/minimal_document.pdf"
        )
        # Assert that the object is correctly initialized with defaults or None for optional parameters
        assert source_doc.content == "Minimal content example"
        assert source_doc.source == "https://example.com/minimal_document.pdf"
        assert source_doc.id is None
        assert source_doc.title is None
        assert source_doc.chunk is None
        assert source_doc.offset is None
        assert source_doc.page_number is None
        assert source_doc.container_name is None
        assert source_doc.global_business is None
        assert source_doc.divisions_and_areas is None
        assert source_doc.tags is None
        assert source_doc.region is None
        assert source_doc.country is None
        assert source_doc.language is None
        assert source_doc.year is None
        assert source_doc.period is None
        assert source_doc.importance is None
        assert source_doc.security is None
        assert source_doc.origin is None
        assert source_doc.domain is None

    def test_to_json(self):
        doc = SourceDocument(content='Lorem ipsum', source='example.com', id='123')
        json_str = doc.to_json()
        assert isinstance(json_str, str)
    
    def test_from_json(self):
        json_str = '''{
                        "id": "123",
                        "content": "Lorem ipsum",
                        "source": "example.com",
                        "title": "Test Title",
                        "chunk": "Test Chunk",
                        "offset": 0,
                        "page_number": 1,
                        "container_name": "Test Container",
                        "global_business": "Test Business",
                        "divisions_and_areas": "Test Division",
                        "tags": "Test Tags",
                        "region": "Test Region",
                        "country": "Test Country",
                        "language": "Test Language",
                        "year": "2022",
                        "period": "Test Period",
                        "importance": "High",
                        "security": "Test Security",
                        "origin": "Test Origin",
                        "domain": "Test Domain"
                    }'''
        doc = SourceDocument.from_json(json_str)
        assert isinstance(doc, SourceDocument)
        assert doc.id == '123'
        assert doc.content == 'Lorem ipsum'
        assert doc.source == 'example.com'
    
    def test_from_dict(self):
        dict_obj = {"id": "123",
                    "content": "Lorem ipsum",
                    "source": "example.com",
                    "title": "Test Title",
                    "chunk": "Test Chunk",
                    "offset": 0,
                    "page_number": 1,
                    "container_name": "Test Container",
                    "global_business": "Test Business",
                    "divisions_and_areas": "Test Division",
                    "tags": "Test Tags",
                    "region": "Test Region",
                    "country": "Test Country",
                    "language": "Test Language",
                    "year": "2022",
                    "period": "Test Period",
                    "importance": "High",
                    "security": "Test Security",
                    "origin": "Test Origin",
                    "domain": "Test Domain"}
        doc = SourceDocument.from_dict(dict_obj)
        assert isinstance(doc, SourceDocument)
        assert doc.title == "Test Title"
        assert doc.language == "Test Language"
        assert doc.chunk == "Test Chunk"
    
    def test_get_filename(self):
        doc = SourceDocument(content='Lorem ipsum', source='example.com')
        filename = doc.get_filename()
        assert isinstance(filename, str)
        assert filename == 'example'
    
    def test_convert_to_langchain_document(self):
        doc = SourceDocument(content='Lorem ipsum', source='example.com')
        langchain_doc = doc.convert_to_langchain_document()
        assert langchain_doc.page_content == 'Lorem ipsum'
        assert langchain_doc.metadata['id'] == None
        assert langchain_doc.metadata['source'] == 'example.com'
        assert langchain_doc.metadata['title'] == None
        assert langchain_doc.metadata['chunk'] == None
        assert langchain_doc.metadata['offset'] == None
        assert langchain_doc.metadata['page_number'] == None
        assert langchain_doc.metadata['global_business'] == None
        assert langchain_doc.metadata['divisions_and_areas'] == None
        assert langchain_doc.metadata['tags'] == None
        assert langchain_doc.metadata['region'] == None
        assert langchain_doc.metadata['country'] == None
        assert langchain_doc.metadata['language'] == None
        assert langchain_doc.metadata['year'] == None
        assert langchain_doc.metadata['period'] == None
        assert langchain_doc.metadata['importance'] == None
        assert langchain_doc.metadata['security'] == None
        assert langchain_doc.metadata['origin'] == None
        assert langchain_doc.metadata['domain'] == None