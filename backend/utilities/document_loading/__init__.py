"""
This module manages loading settings and provides functions for retrieving class names defined in the module.
"""
import os
from typing import List
import os.path
import pkgutil
from .Strategies import LoadingStrategy, get_document_loader

class LoadingSettings:
    """
    Class for managing loading settings.
    Parameters:
        loading (dict): A dictionary containing loading settings.
    Attributes:
        loading_strategy (LoadingStrategy): The configured loading strategy.
    """
    def __init__(self, loading):
        self.loading_strategy = LoadingStrategy(loading['strategy'])

def get_all_classes() -> List[str]:
    """
    Get a list of all class names defined in the current module.
    Returns:
        List[str]: A list of class names.
    """
    return [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)])]

__all__ = get_all_classes()