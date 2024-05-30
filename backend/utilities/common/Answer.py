'''
This file defines the Answer class, which represents an answer to a question.
Provides methods to convert the response to JSON format and vice versa.
'''
import json
from typing import List, Optional
from .SourceDocument import SourceDocument

class Answer:
    """
    Class representing an answer.
    """
    def __init__(self, question: str, answer: str, source_documents: List[SourceDocument] = [], prompt_tokens: Optional[int] = 0, completion_tokens: Optional[int] = 0):
        """
        Initialize an Answer instance.
        Parameters:
            question (str): The question.
            answer (str): The answer.
            source_documents (List[SourceDocument], optional): A list of source documents. Defaults to an empty list.
            prompt_tokens (Optional[int], optional): The number of prompt tokens. Defaults to 0.
            completion_tokens (Optional[int], optional): The number of completion tokens. Defaults to 0.
        """
        self.question = question
        self.answer = answer
        self.source_documents = source_documents if source_documents is not None else []
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        
    def to_json(self):
        """
        Serialize the Answer instance to JSON.
        Returns:
            str: The JSON string representation of the Answer.
        """
        return json.dumps(self, cls=AnswerEncoder)
    
    @classmethod
    def from_json(cls, json_string):
        """
        Deserialize an Answer instance from JSON.
        Parameters:
            json_string (str): The JSON string representation of the Answer.
        Returns:
            Answer: The deserialized Answer instance.
        """
        return json.loads(json_string, cls=AnswerDecoder)

class AnswerEncoder(json.JSONEncoder):
    """
    JSON encoder for the Answer class.
    """
    def default(self, obj):
        """
        Encode the Answer instance to JSON.
        Parameters:
            obj (object): The object to encode.
        Returns:
            dict: The JSON-compatible representation of the object.
        """
        if isinstance(obj, Answer):
            return {
                'question': obj.question,
                'answer': obj.answer,
                'source_documents': [doc.to_json() for doc in obj.source_documents],
                'prompt_tokens': obj.prompt_tokens,
                'completion_tokens': obj.completion_tokens
            }
        return super().default(obj)
    
class AnswerDecoder(json.JSONDecoder):
    """
    JSON decoder for the Answer class.
    """
    def decode(self, s, **kwargs):
        """
        Decode JSON to an Answer instance.
        Parameters:
            s (str): The JSON string to decode.
        Returns:
            Answer: The deserialized Answer instance.
        """
        obj = super().decode(s, **kwargs)
        return Answer(
            question=obj['question'],
            answer=obj['answer'],
            source_documents=[SourceDocument.from_json(doc) for doc in obj['source_documents']],
            prompt_tokens=obj['prompt_tokens'],
            completion_tokens=obj['completion_tokens']
        )