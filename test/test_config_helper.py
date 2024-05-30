import pytest, json
from unittest.mock import patch, MagicMock
from backend.utilities.helpers.ConfigHelper import ConfigHelper, Metadata, Prompts

class TestConfigHelper:
    @pytest.fixture
    def blob_client_mock(self):
        with patch('backend.utilities.helpers.ConfigHelper.AzureBlobStorageClient') as mock_blob_client:
            yield mock_blob_client

    @pytest.fixture
    def config_mock(self):
        return MagicMock()
    
    @pytest.fixture
    def prompts(self):
        return Prompts({
            'condense_question_prompt': 'Condense question prompt',
            'answering_prompt': 'Answering prompt',
            'post_answering_prompt': 'Post answering prompt',
            'enable_post_answering_prompt': True,
            'faq_answering_prompt': 'FAQ answering prompt',
            'faq_content': 'FAQ content'
        })


    @pytest.fixture
    def default_config_mock(self):
        return {"default_key": "default_value"}
    
    @pytest.fixture
    def config_helper(self):
        return ConfigHelper()
    
    @pytest.fixture
    def metadata(self):
        metadata_data = {
            "global_business": ["business1", "business2"],
            "divisions_and_areas": ["division1", "division2"],
            "tags": ["tag1", "tag2"],
            "regions_and_countries": ["region1", "region2"],
            "languages": ["language1", "language2"],
            "years": [2020, 2021],
            "periods": ["Q1", "Q2"],
            "importances": ["high", "low"],
            "securities": ["security1", "security2"],
            "origins": ["origin1", "origin2"],
            "domains": ["domain1", "domain2"]
        }
        return Metadata(metadata_data)

    def test_get_active_config_or_default_success(self, blob_client_mock, config_mock, default_config_mock):
        blob_client_mock.return_value.download_file.return_value = '{"key": "value"}'
        config_mock.return_value = {"key": "value"}

        with patch('backend.utilities.helpers.ConfigHelper.Config', config_mock):
            with patch('backend.utilities.helpers.ConfigHelper.ConfigHelper.get_default_config', return_value=default_config_mock):
                result = ConfigHelper.get_active_config_or_default()

        assert result == {"key": "value"}

    def test_get_active_config_or_default_exception(self, blob_client_mock, config_mock, default_config_mock):
        blob_client_mock.return_value.download_file.side_effect = Exception("Blob storage error")
        config_mock.return_value = {"default_key": "default_value"}

        with patch('backend.utilities.helpers.ConfigHelper.Config', config_mock):
            with patch('backend.utilities.helpers.ConfigHelper.ConfigHelper.get_default_config', return_value=default_config_mock):
                result = ConfigHelper.get_active_config_or_default()

        assert result == {"default_key": "default_value"}

    def test_save_config_as_active_success(self, blob_client_mock):
        config = {"key": "value"}
        
        ConfigHelper.save_config_as_active(config)
        
        blob_client_mock.return_value.upload_file.assert_called_once_with(
            json.dumps(config, indent=2), "active.json", content_type='application/json'
        )
        
    def test_metadata_initialization(self, metadata):
        assert metadata.global_business == ["business1", "business2"]
        assert metadata.divisions_and_areas == ["division1", "division2"]
        assert metadata.tags == ["tag1", "tag2"]
        assert metadata.regions_and_countries == ["region1", "region2"]
        assert metadata.languages == ["language1", "language2"]
        assert metadata.years == [2020, 2021]
        assert metadata.periods == ["Q1", "Q2"]
        assert metadata.importances == ["high", "low"]
        assert metadata.securities == ["security1", "security2"]
        assert metadata.origins == ["origin1", "origin2"]
        assert metadata.domains == ["domain1", "domain2"]
        
    def test_prompts_initialization(self, prompts):
        assert prompts.condense_question_prompt == 'Condense question prompt'
        assert prompts.answering_prompt == 'Answering prompt'
        assert prompts.post_answering_prompt == 'Post answering prompt'
        assert prompts.enable_post_answering_prompt == True
        assert prompts.faq_answering_prompt == 'FAQ answering prompt'
        assert prompts.faq_content == 'FAQ content'