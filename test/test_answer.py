from backend.utilities.common.SourceDocument import SourceDocument
from backend.utilities.common.Answer import Answer
import json

class TestAnswer: 
    def test_serialize_answer_with_all_fields(self):

            # Create a source document
            source_doc = SourceDocument("Content of the document", "http://example.com")
            # Create an Answer instance with all fields
            answer = Answer("What is the capital of France?", "Paris", [source_doc], 10, 20)
            # Serialize the Answer instance
            json_string = answer.to_json()
            # Assert the JSON string is not empty and contains key parts of the data
            assert json_string is not None
            assert "What is the capital of France?" in json_string
            assert "Paris" in json_string
            assert "http://example.com" in json_string
            assert '"prompt_tokens": 10' in json_string
            assert '"completion_tokens": 20' in json_string
    
    def test_initialize_answer_with_empty_strings(self):
        # Initialize an Answer instance with empty strings for question and answer
        answer = Answer("", "")
        # Assert that the question and answer are indeed empty strings
        assert answer.question == ""
        assert answer.answer == ""