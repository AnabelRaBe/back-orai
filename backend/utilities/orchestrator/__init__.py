"""
This module provides utilities for orchestrating processes.
"""
import os
from typing import List
import os.path
import pkgutil
from .Strategies import OrchestrationStrategy, get_orchestrator

class OrchestrationSettings:
    """
    Class for managing orchestration settings.
    Parameters:
        orchestration (dict): A dictionary containing orchestration settings.
    Attributes:
        strategy (OrchestrationStrategy): The configured orchestration strategy.
    """
    def __init__(self, orchestration: dict):
        self.strategy = OrchestrationStrategy(orchestration['strategy'])

def get_all_classes() -> List[str]:
    """
    Get a list of all class names defined in the current module.
    Returns:
        List[str]: A list of class names.
    """
    return [name for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)])]

__all__ = get_all_classes()