import pytest
from unittest.mock import patch
from backend.utilities.helpers.EnvHelper import EnvHelper

class TestEnvHelper:
    
    @pytest.fixture
    def mock_env_vars(self):
        env_vars = {
            # Azure Search
            'AZURE_SEARCH_SERVICE': 'search_service',
            'AZURE_SEARCH_INDEX': 'search_index',
            'AZURE_INGEST_INDEX': 'ingest_index',
            'AZURE_SEARCH_KEY': 'azure_search_key',
            'AZURE_SEARCH_USE_SEMANTIC_SEARCH': 'use_semantic_search',
            'AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG': 'semantic_search_config',
            'AZURE_SEARCH_INDEX_IS_PRECHUNKED': 'index_is_prechunked',
            'AZURE_SEARCH_TOP_K': 'top_k',
            'AZURE_SEARCH_ENABLE_IN_DOMAIN': 'enable_in_domain',
            'AZURE_SEARCH_FIELDS_ID': 'fields_id',
            'AZURE_SEARCH_CONTENT_COLUMNS': 'content_columns',
            'AZURE_SEARCH_CONTENT_VECTOR_COLUMNS': 'content_vector_columns',
            'AZURE_SEARCH_DIMENSIONS': 'dimensions',
            'AZURE_SEARCH_FILENAME_COLUMN': 'filename_column',
            'AZURE_SEARCH_TITLE_COLUMN': 'title_column',
            'AZURE_SEARCH_URL_COLUMN': 'url_column',
            'AZURE_SEARCH_FIELDS_TAG': 'fields_tag',
            'AZURE_SEARCH_FIELDS_METADATA': 'fields_metadata',
            'AZURE_SEARCH_CONVERSATIONS_LOG_INDEX': 'conversations_log_index',
            # Azure OpenAI
            'AZURE_OPENAI_RESOURCE': 'openai_resource',
            'AZURE_OPENAI_MODEL': 'openai_model',
            'AZURE_OPENAI_KEY': 'openai_key',
            'AZURE_OPENAI_MODEL_NAME': 'openai_model_name',
            'AZURE_OPENAI_TEMPERATURE': 'openai_temperature',
            'AZURE_OPENAI_TOP_P': 'openai_top_p',
            'AZURE_OPENAI_MAX_TOKENS': 'max_tokens',
            'AZURE_OPENAI_STOP_SEQUENCE': 'stop_sequence',
            'AZURE_OPENAI_SYSTEM_MESSAGE': 'system_message',
            'AZURE_OPENAI_API_VERSION': 'api_version',
            'AZURE_OPENAI_STREAM': 'openai_stream',
            'AZURE_OPENAI_EMBEDDING_MODEL': 'embedding_model',
            # Set env for OpenAI SDK
            'OPENAI_API_TYPE': 'azure',
            'OPENAI_API_BASE': 'https://openai_resource.openai.azure.com/',
            'OPENAI_API_KEY': 'openai_key',
            'OPENAI_API_VERSION': 'azure_openai_api_version',
            # Azure Functions - Batch processing
            'BACKEND_URL': 'backend_url',
            'AzureWebJobsStorage': 'webjobs_storage',
            'DOCUMENT_PROCESSING_QUEUE_NAME': 'processing_queue_name',
            # Azure Blob Storage
            'AZURE_BLOB_ACCOUNT_NAME': 'blob_account_name',
            'AZURE_BLOB_ACCOUNT_KEY': 'blob_account_key',
            'AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME': 'global_documents_container',
            'AZURE_BLOB_LOCAL_DOCUMENTS_CONTAINER_NAME': 'local_documents_container',
            # Azure Form Recognizer
            'AZURE_FORM_RECOGNIZER_ENDPOINT': 'form_recognizer_endpoint',
            'AZURE_FORM_RECOGNIZER_KEY': 'form_recognizer_key',
            # Azure App Insights
            'APPINSIGHTS_CONNECTION_STRING': 'appinsights_connection_string',
            # Orchestration Settings
            'ORCHESTRATION_STRATEGY': 'orchestration_strategy'
        }
        with patch.dict('os.environ', env_vars):
            yield

    def test_azure_search_service(self, mock_env_vars):
        env_helper = EnvHelper()
        #Azure Search
        assert env_helper.AZURE_SEARCH_SERVICE == 'search_service'
        assert env_helper.AZURE_SEARCH_INDEX == 'search_index'
        assert env_helper.AZURE_INGEST_INDEX == 'ingest_index'
        assert env_helper.AZURE_SEARCH_KEY == 'azure_search_key'
        assert env_helper.AZURE_SEARCH_USE_SEMANTIC_SEARCH == 'use_semantic_search'
        assert env_helper.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG == 'semantic_search_config'
        assert env_helper.AZURE_SEARCH_INDEX_IS_PRECHUNKED == 'index_is_prechunked'
        assert env_helper.AZURE_SEARCH_TOP_K == 'top_k'
        assert env_helper.AZURE_SEARCH_ENABLE_IN_DOMAIN == 'enable_in_domain'
        assert env_helper.AZURE_SEARCH_FIELDS_ID == 'fields_id'
        assert env_helper.AZURE_SEARCH_CONTENT_COLUMNS == 'content_columns'
        assert env_helper.AZURE_SEARCH_CONTENT_VECTOR_COLUMNS == 'content_vector_columns'
        assert env_helper.AZURE_SEARCH_DIMENSIONS == 'dimensions'
        assert env_helper.AZURE_SEARCH_FILENAME_COLUMN == 'filename_column'
        assert env_helper.AZURE_SEARCH_TITLE_COLUMN == 'title_column'
        assert env_helper.AZURE_SEARCH_URL_COLUMN == 'url_column'
        assert env_helper.AZURE_SEARCH_FIELDS_TAG == 'fields_tag'
        assert env_helper.AZURE_SEARCH_FIELDS_METADATA == 'fields_metadata'
        assert env_helper.AZURE_SEARCH_CONVERSATIONS_LOG_INDEX == 'conversations_log_index'
        # Azure OpenAI
        assert env_helper.AZURE_OPENAI_RESOURCE == 'openai_resource'
        assert env_helper.AZURE_OPENAI_MODEL == 'openai_model'
        assert env_helper.AZURE_OPENAI_KEY == 'openai_key'
        assert env_helper.AZURE_OPENAI_MODEL_NAME == 'openai_model_name'
        assert env_helper.AZURE_OPENAI_TEMPERATURE == 'openai_temperature'
        assert env_helper.AZURE_OPENAI_TOP_P == 'openai_top_p'
        assert env_helper.AZURE_OPENAI_MAX_TOKENS == 'max_tokens'
        assert env_helper.AZURE_OPENAI_STOP_SEQUENCE == 'stop_sequence'
        assert env_helper.AZURE_OPENAI_SYSTEM_MESSAGE == 'system_message'
        assert env_helper.AZURE_OPENAI_API_VERSION == 'api_version'
        assert env_helper.AZURE_OPENAI_STREAM == 'openai_stream'
        assert env_helper.AZURE_OPENAI_EMBEDDING_MODEL == 'embedding_model'
        # Set env for OpenAI SDK
        assert env_helper.OPENAI_API_TYPE == 'azure'
        assert env_helper.OPENAI_API_BASE == 'https://openai_resource.openai.azure.com/'
        # Azure Functions - Batch processing
        assert env_helper.BACKEND_URL == 'backend_url'
        assert env_helper.AzureWebJobsStorage == 'webjobs_storage'
        assert env_helper.DOCUMENT_PROCESSING_QUEUE_NAME == 'processing_queue_name'
        # Azure Blob Storage
        assert env_helper.AZURE_BLOB_ACCOUNT_NAME == 'blob_account_name'
        assert env_helper.AZURE_BLOB_ACCOUNT_KEY == 'blob_account_key'
        assert env_helper.AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME == 'global_documents_container'
        assert env_helper.AZURE_BLOB_LOCAL_DOCUMENTS_CONTAINER_NAME == 'local_documents_container'
        # Azure Form Recognizer
        assert env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT == 'form_recognizer_endpoint'
        assert env_helper.AZURE_FORM_RECOGNIZER_KEY == 'form_recognizer_key'
        # Azure App Insights
        assert env_helper.APPINSIGHTS_CONNECTION_STRING == 'appinsights_connection_string'
        # Orchestration Settings
        assert env_helper.ORCHESTRATION_STRATEGY == 'orchestration_strategy'
