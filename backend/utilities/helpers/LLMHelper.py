"""
LLMHelper
"""
import openai
from typing import List
from .EnvHelper import EnvHelper
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class LLMHelper:
    """
    Helper class for managing OpenAI language models (LLMs).
    """
    def __init__(self):
        """
        Initialize the LLMHelper.
        """
        env_helper: EnvHelper = EnvHelper()

        # Configure OpenAI API
        openai.api_type = "azure"
        openai.api_version = env_helper.AZURE_OPENAI_API_VERSION
        openai.api_base = env_helper.OPENAI_API_BASE
        openai.api_key = env_helper.OPENAI_API_KEY

        self.llm_model = env_helper.AZURE_OPENAI_MODEL
        self.llm_max_tokens = env_helper.AZURE_OPENAI_MAX_TOKENS if env_helper.AZURE_OPENAI_MAX_TOKENS != '' else None
        self.embedding_model = env_helper.AZURE_OPENAI_EMBEDDING_MODEL

    def get_llm(self, deployment_name: str, temperature: float, max_tokens: int):
        """
        Get an instance of the AzureChatOpenAI class for interacting with a language model.
        Parameters:
            deployment_name (str): The deployment name of the language model.
            temperature (float): The temperature parameter for model sampling.
            max_tokens (int): The maximum number of tokens for model completion.
        Returns:
            AzureChatOpenAI: An instance of the AzureChatOpenAI class.
        """
        return AzureChatOpenAI(deployment_name=deployment_name, temperature=temperature, max_tokens=max_tokens, openai_api_version=openai.api_version)

    def get_streaming_llm(self, deployment_name: str, temperature: float, max_tokens: int):
        """
        Get an instance of the AzureChatOpenAI class with streaming capabilities.
        Parameters:
            deployment_name (str): The deployment name of the language model.
            temperature (float): The temperature parameter for model sampling.
            max_tokens (int): The maximum number of tokens for model completion.
        Returns:
            AzureChatOpenAI: An instance of the AzureChatOpenAI class with streaming capabilities.
        """
        return AzureChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler], deployment_name=deployment_name, temperature=temperature,max_tokens=max_tokens, openai_api_version=openai.api_version)

    def get_embedding_model(self):
        """
        Get an instance of the OpenAIEmbeddings class for working with embeddings.
        Returns:
            OpenAIEmbeddings: An instance of the OpenAIEmbeddings class.
        """
        return OpenAIEmbeddings(deployment=self.embedding_model, chunk_size=1)

    def get_chat_completion_with_functions(self, messages: List[dict], functions: List[dict], function_call: str="auto"):
        """
        Get chat completion with function execution.
        Parameters:
            messages (List[dict]): List of message dictionaries.
            functions (List[dict]): List of function dictionaries.
            function_call (str, optional): Function call mode. Defaults to "auto".
        Returns:
            openai.ChatCompletion: Chat completion response.
        """
        return openai.ChatCompletion.create(
            deployment_id=self.llm_model,
            messages=messages,
            functions=functions,
            function_call=function_call,
            )

    def get_chat_completion(self, messages: List[dict]):
        """
        Get chat completion.
        Parameters:
            messages (List[dict]): List of message dictionaries.
        Returns:
            openai.ChatCompletion: Chat completion response.
        """
        return openai.ChatCompletion.create(deployment_id=self.llm_model,messages=messages,)