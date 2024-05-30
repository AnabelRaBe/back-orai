"""
This module provides functionality related to importing classes dynamically and getting a list of all class names defined in the current module.
"""
import os
from enum import Enum
from typing import List
import os.path
import pkgutil
from .Strategies import ChunkingSettings, ChunkingStrategy, get_document_chunker

def get_all_classes() -> List[str]:
    """
    Get a list of all class names defined in the current module.
    Returns:
        List[str]: A list of class names.
    """
    return [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)])]

__all__ = get_all_classes()