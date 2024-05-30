import pytest
from unittest.mock import patch
from backend.utilities.parser.OutputParserTool import OutputParserTool
from backend.utilities.common.SourceDocument import SourceDocument

class TestOutputParserTool:

    # @patch('backend.utilities.parser.OutputParserTool.OutputParserTool._clean_up_answer')
    # @patch('backend.utilities.parser.OutputParserTool.OutputParserTool._get_source_docs_from_answer')
    # @patch('backend.utilities.parser.OutputParserTool.OutputParserTool._make_doc_references_sequential')
    # def test_parse(self, mock_clean_up_answer, mock_get_source_docs_from_answer, mock_make_doc_references_sequential):
    #     # Create a mock question, answer, and source documents
    #     question = "What is the answer?"
    #     answer = "The answer is [doc1] and [doc2]."
    #     source_documents = [
    #         SourceDocument(content="Document 1 content", id="doc1", source="source1"),
    #         SourceDocument(content="Document 2 content", id="doc2", source="source2")
    #     ]

    #     # Create an instance of OutputParserTool
    #     parser = OutputParserTool()

    #     # Mock the internal methods
    #     mock_clean_up_answer.return_value = "The answer is [doc1] and [doc2]."
    #     mock_get_source_docs_from_answer.return_value = [1, 2]
    #     mock_make_doc_references_sequential.return_value = "The answer is [doc1] and [doc2]."

    #     # Call the parse method
    #     result = parser.parse(question, answer, source_documents)

    #     # Assert the result
    #     assert len(result) == 2
    #     assert result[0]["role"] == "tool"
    #     assert result[0]["content"]["citations"][0]["content"] == "Document 1 content"
    #     assert result[0]["content"]["citations"][0]["id"] == "doc1"
    #     assert result[0]["content"]["citations"][0]["chunk_id"] is None
    #     assert result[0]["content"]["citations"][0]["title"] is None
    #     assert result[0]["content"]["citations"][0]["filepath"] is None
    #     assert result[0]["content"]["citations"][0]["url"] is None
    #     assert result[0]["content"]["citations"][0]["page_number"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["offset"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["source"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["markdown_url"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["title"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["original_url"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["chunk"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["key"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["filename"] is None
    #     assert result[0]["content"]["citations"][0]["metadata"]["page_number"] is None
    #     assert result[0]["content"]["citations"][0]["container_name"] is None
    #     assert result[1]["role"] == "assistant"
    #     assert result[1]["content"] == "The answer is [doc1] and [doc2]."
    #     assert result[1]["end_turn"] is True

    def test_clean_up_answer(self):
        # Create an instance of OutputParserTool
        parser = OutputParserTool()

        # Call the _clean_up_answer method
        result = parser._clean_up_answer("The  answer  is  correct.")

        # Assert the result
        assert result == "The answer is correct."

    def test_get_source_docs_from_answer(self):
        # Create an instance of OutputParserTool
        parser = OutputParserTool()

        # Call the _get_source_docs_from_answer method
        result = parser._get_source_docs_from_answer("The answer is [doc1] and [doc2].")

        # Assert the result
        assert result == [1, 2]

    def test_make_doc_references_sequential(self):
        # Create an instance of OutputParserTool
        parser = OutputParserTool()

        # Call the _make_doc_references_sequential method
        result = parser._make_doc_references_sequential("The answer is [doc1] and [doc2].", [1, 2])

        # Assert the result
        assert result == "The answer is [doc1] and [doc2]."