"""
LoadingStrategy
"""

from enum import Enum  

class LoadingStrategy(Enum):
    """
    Enumeration class for loading strategies.
    """
    layout = 'layout'
    read = 'read'
    web = 'web'
    docx = 'docx'

def get_document_loader(loader_strategy: str):
    """
    Get the document loader based on the specified strategy.
    Parameters:
        loader_strategy (str): The selected loader strategy.
    Returns:
        object: An instance of the document loader.
    Raises:
        Exception: If the loader strategy is unknown.
    """
    if loader_strategy == LoadingStrategy.layout.value:
        # Importing LayoutDocumentLoading class dynamically
        from .Layout import LayoutDocumentLoading  
        return LayoutDocumentLoading()
    elif loader_strategy == LoadingStrategy.read.value:
        # Importing ReadDocumentLoading class dynamically
        from .Read import ReadDocumentLoading  
        return ReadDocumentLoading()
    elif loader_strategy == LoadingStrategy.web.value:
        # Importing WebDocumentLoading class dynamically
        from .Web import WebDocumentLoading  
        return WebDocumentLoading()
    elif loader_strategy == LoadingStrategy.docx.value:
        # Importing WordDocumentLoading class dynamically
        from .WordDocument import WordDocumentLoading  
        return WordDocumentLoading()
    else:
        raise Exception(f"Unknown loader strategy: {loader_strategy}")
