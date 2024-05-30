"""
Defines an enumeration for orchestration strategies and a function to get an orchestrator based on the strategy.
"""
from enum import Enum

class OrchestrationStrategy(Enum):
    """
    Enumeration class for orchestration strategies.
    """
    openai_function = 'openai_function'
    langchain = 'langchain'

def get_orchestrator(orchestration_strategy: str, language: str, global_index_name: str, user_index_name: str):
    """
    Get the orchestrator based on the specified strategy.
    Parameters:
        orchestration_strategy (str): The selected orchestration strategy.
        language (str): The language for the orchestrator.
        global_index_name (str): The global index name.
        user_index_name (str): The user index name.
    Returns:
        object: An instance of the orchestrator.
    Raises:
        Exception: If the orchestration strategy is unknown.
    """
    if orchestration_strategy == OrchestrationStrategy.langchain.value:
        from .LangChainAgent import LangChainAgent
        return LangChainAgent(language, global_index_name, user_index_name)
    else:
        raise Exception(f"Unknown orchestration strategy: {orchestration_strategy}")
