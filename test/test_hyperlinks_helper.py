import pytest
from unittest.mock import patch, MagicMock
from backend.utilities.helpers.HyperlinksHelper import Hyperlinks

class TestHyperlinks:
    @pytest.fixture
    def hyperlinks(self):
        return Hyperlinks()

    def test_generate_references(self, hyperlinks):
        result = {
            'choices': [
                {
                    'messages': [
                        {
                            'content': '{"citations": ["source1", "source2"]}'
                        }
                    ]
                }
            ]
        }

        references = hyperlinks.generate_references(result)

        assert references == ["source1", "source2"]

    def test_add_hyperlinks(self, hyperlinks):
        response = {
            'choices': [
                {
                    'messages': [
                        {
                            'content': '{"citations": [{"url": "https://example.com/1"}, {"url": "https://example.com/2"}]}'
                        }
                    ]
                }
            ]
        }
        answer_without_followup = "This is a [link1] and [link2]"

        result = hyperlinks.add_hyperlinks(response, answer_without_followup)

        assert result == "This is a [https://example.com/1] and [https://example.com/2]"