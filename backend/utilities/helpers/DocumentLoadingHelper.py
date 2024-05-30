"""
This class manages the loading of documents from various sources.
"""
from typing import List
from langchain.docstore.document import Document
from ..document_loading import get_document_loader, LoadingSettings, LoadingStrategy

class DocumentLoading:
    """
    Class for loading documents.
    """
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass
    
    def load(self, document_url: str, loading: LoadingSettings, metadata: dict) -> List[Document]:
        """
        Load documents from the given URL.
        Parameters:
            document_url (str): The URL of the document to load.
            loading (LoadingSettings): The loading settings.
            metadata (dict): Additional metadata for loading.
        Returns:
            List[Document]: A list of loaded documents.
        Raises:
            ValueError: If the loader strategy is unknown.
        """
        loader = get_document_loader(loader_strategy=loading.loading_strategy.value)
        if loader is None:
            raise ValueError(f"Unknown loader strategy: {loading.loading_strategy.value}")
        return loader.load(document_url=document_url,
                           metadata=metadata)