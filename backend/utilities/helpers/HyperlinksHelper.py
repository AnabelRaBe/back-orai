"""
In this module hyperlinks are managed.
"""
import os  
import regex as re  
import json  

class Hyperlinks:
    """
    Class for managing hyperlinks in responses.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass

    def generate_references(self, result) -> list:
        """
        Generate references from the OpenAI response.
        Parameters:
            result: The OpenAI response.
        Returns:
            list: List of references.
        """
        content = json.loads(result['choices'][0]['messages'][0]['content'])
        preview = [source for source in content['citations']]
        return preview

    def add_hyperlinks(self, response, answer_without_followup: str, ) -> str:
        """
        Add hyperlinks to the answer.
        Parameters:
            response: The OpenAI response.
            answer_without_followup (str): The answer without follow-up.
        Returns:
            str: The answer with hyperlinks added.
        """
        references = self.generate_references(response)

        urls = [source["url"] for source in references]
        regex = r'\[([^]]+)\]'

        results = re.findall(regex, answer_without_followup)
        references_ids = [re.findall("\d+", value)[0] for value in results]
        links = [urls[int(id)-1] for id in references_ids]

        container_name = os.environ.get('AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME', 'documents2')
        for i, link in enumerate(links):
            modified_link = re.sub(f'/{re.escape(container_name)}/', '', link, count=1)
            answer_without_followup = answer_without_followup.replace(results[i], f"{modified_link}")


        return answer_without_followup