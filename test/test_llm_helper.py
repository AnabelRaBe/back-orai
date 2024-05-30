import pytest
from unittest.mock import patch, MagicMock
from backend.utilities.helpers.LLMHelper import LLMHelper
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  

@pytest.fixture
def mock_env_helper():
    with patch('backend.utilities.helpers.LLMHelper.EnvHelper') as MockEnvHelper:
        mock_env_helper = MockEnvHelper.return_value
        mock_env_helper.AZURE_OPENAI_API_VERSION = "v1"
        mock_env_helper.OPENAI_API_BASE = "https://api.openai.com"
        mock_env_helper.OPENAI_API_KEY = "test_key"
        mock_env_helper.AZURE_OPENAI_MODEL = "test_model"
        mock_env_helper.AZURE_OPENAI_MAX_TOKENS = 100
        mock_env_helper.AZURE_OPENAI_EMBEDDING_MODEL = "embedding_model"
        yield mock_env_helper

@pytest.fixture
def llm_helper(mock_env_helper):
    return LLMHelper()

def test_get_llm(llm_helper):
    with patch('backend.utilities.helpers.LLMHelper.AzureChatOpenAI') as MockAzureChatOpenAI:
        deployment_name = "test_deployment"
        temperature = 0.7
        max_tokens = 50
        llm_helper.get_llm(deployment_name, temperature, max_tokens)
        MockAzureChatOpenAI.assert_called_once_with(deployment_name=deployment_name, temperature=temperature, max_tokens=max_tokens, openai_api_version="v1")

def test_get_streaming_llm(llm_helper):
    with patch('backend.utilities.helpers.LLMHelper.AzureChatOpenAI') as MockAzureChatOpenAI:
        deployment_name = "test_deployment"
        temperature = 0.7
        max_tokens = 50
        llm_helper.get_streaming_llm(deployment_name, temperature, max_tokens)
        MockAzureChatOpenAI.assert_called_once_with(streaming=True, callbacks=[StreamingStdOutCallbackHandler], deployment_name=deployment_name, temperature=temperature, max_tokens=max_tokens, openai_api_version="v1")

def test_get_embedding_model(llm_helper):
    with patch('backend.utilities.helpers.LLMHelper.OpenAIEmbeddings') as MockOpenAIEmbeddings:
        llm_helper.get_embedding_model()
        MockOpenAIEmbeddings.assert_called_once_with(deployment="embedding_model", chunk_size=1)

def test_get_chat_completion_with_functions(llm_helper):
    with patch('openai.ChatCompletion.create') as mock_create:
        messages = [{"role": "user", "content": "Hello"}]
        functions = [{"name": "test_function", "description": "A test function"}]
        function_call = "auto"
        llm_helper.get_chat_completion_with_functions(messages, functions, function_call)
        mock_create.assert_called_once_with(deployment_id="test_model", messages=messages, functions=functions, function_call=function_call)

def test_get_chat_completion(llm_helper):
    with patch('openai.ChatCompletion.create') as mock_create:
        messages = [{"role": "user", "content": "Hello"}]
        llm_helper.get_chat_completion(messages)
        mock_create.assert_called_once_with(deployment_id="test_model", messages=messages)