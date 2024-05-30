import pytest
from unittest.mock import MagicMock, patch
from backend.utilities.tools.GenerateTopicTool import GenerateTopicTool

class TestGenerateTopicTool:
    @pytest.fixture
    def mock_env_helper(self):
        mock_env_helper = MagicMock()
        mock_env_helper.AZURE_OPENAI_API_VERSION = "v1"
        mock_env_helper.OPENAI_API_BASE = "https://api.openai.com"
        mock_env_helper.OPENAI_API_KEY = "your-api-key"
        return mock_env_helper

    @pytest.fixture
    def mock_llm_helper(self):
        return MagicMock()

    @pytest.fixture
    def mock_config_helper(self):
        mock_config_helper = MagicMock()
        mock_config_helper.get_active_config_or_default.return_value = {
            "llm": {
                "model": "your-llm-model",
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        return mock_config_helper

    @pytest.fixture
    def mock_generate_topic_tool(self, mock_env_helper, mock_llm_helper, mock_config_helper):
        with patch("backend.utilities.tools.GenerateTopicTool.EnvHelper", return_value=mock_env_helper), \
             patch("backend.utilities.tools.GenerateTopicTool.LLMHelper", return_value=mock_llm_helper), \
             patch("backend.utilities.tools.GenerateTopicTool.ConfigHelper", return_value=mock_config_helper):
            return GenerateTopicTool()

    def test_generate_topic(self, mock_generate_topic_tool):
        content = ["content1", "content2"]
        language = "en"
        result_text = "Generated topic"

        mock_result = {"text": result_text}
        mock_topic_generator = MagicMock(return_value=mock_result)

        with patch("backend.utilities.tools.GenerateTopicTool.LLMChain", return_value=mock_topic_generator) as mock_llm_chain, \
             patch("backend.utilities.tools.GenerateTopicTool.get_openai_callback"):
            topic = mock_generate_topic_tool.generate_topic(content, language)

        assert isinstance(topic, str)
        assert topic == result_text