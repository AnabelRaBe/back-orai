"""
This module defines an abstract class for orchestrating conversations.
Attributes:OrchestratorBase: An abstract base class for orchestrating conversations.
"""
from uuid import uuid4
from typing import List, Optional
from abc import ABC, abstractmethod
from ..loggers.TokenLogger import TokenLogger

class OrchestratorBase(ABC):
    """
    Abstract base class for orchestrators.
    """
    def __init__(self) -> None:
        """
        Initializes the OrchestratorBase.
        """
        super().__init__()
        self.message_id = str(uuid4())
        self.tokens = {
            'prompt': 0,
            'completion': 0,
            'total': 0
        }
        self.token_logger : TokenLogger = TokenLogger()
    
    def log_tokens(self, prompt_tokens, completion_tokens):
        """
        Logs the number of tokens used.
        Parameters:
            prompt_tokens (int): Number of tokens used for prompts.
            completion_tokens (int): Number of tokens used for completions.
        """
        self.tokens['prompt'] += prompt_tokens
        self.tokens['completion'] += completion_tokens
        self.tokens['total'] += prompt_tokens + completion_tokens
        
    @abstractmethod
    def orchestrate(self, user_message: str, chat_history: List[dict], conversation_id: Optional[str], config: dict, **kwargs: dict) -> dict:
        """
        Abstract method for orchestrating a conversation.
        Parameters:
            user_message (str): The user's message.
            chat_history (List[dict]): History of the conversation.
            config (dict): Configuration parameters.
            **kwargs (dict): Additional keyword arguments.
        Returns:
            dict: The orchestration result.
        """
        pass
    
    def handle_message(self, user_message: str, chat_history: List[dict], conversation_id: Optional[str], config: dict, **kwargs: Optional[dict]) -> dict:
        """
        Handles a user message and logs token usage.
        Parameters:
            user_message (str): The user's message.
            chat_history (List[dict]): History of the conversation.
            conversation_id (Optional[str]): ID of the conversation.
            config (dict): Configuration parameters.
            **kwargs (Optional[dict]): Additional keyword arguments.
        Returns:
            dict: The result of handling the message.
        """
        result = self.orchestrate(user_message, chat_history, conversation_id, config, **kwargs)
        if config.logging.log_tokens:
            custom_dimensions = {
                "conversation_id": conversation_id,
                "message_id": self.message_id,
                "prompt_tokens": self.tokens['prompt'],
                "completion_tokens": self.tokens['completion'],
                "total_tokens": self.tokens['total']
            }
            self.token_logger.log("Conversation", custom_dimensions=custom_dimensions)
        return result
