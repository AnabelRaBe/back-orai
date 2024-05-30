"""
Abstract base class for answering tools.
"""
from abc import ABC, abstractmethod
from typing import List
from ..common.Answer import Answer

class AnsweringToolBase(ABC):
    """
    Abstract base class for answering tools.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass
    
    @abstractmethod
    def answer_question(self, question: str, chat_history: List[dict], **kwargs: dict) -> Answer:
        """
        Abstract method to answer a question.
        Parameters:
            question (str): The question to answer.
            chat_history (List[dict]): A list of previous chat messages.
            **kwargs (dict): Additional keyword arguments for answering.
        Returns:
            Answer: The answer to the question.
        """
        pass