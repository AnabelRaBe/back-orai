"""
Orchestrator
"""
from typing import List
from typing import Tuple
import regex as re
from langchain.docstore.document import Document
from ..orchestrator import get_orchestrator, OrchestrationSettings, OrchestrationStrategy

class Orchestrator:
    """
    Class for orchestrating interactions between various components of a system.
    This class manages the orchestration of interactions between different components of a system.
    It coordinates the flow of data and operations between these components to achieve specific tasks or goals.
    """
    def __init__(self) -> None:
        """
        Attributes:None
        Methods:__init__: Initializes the Orchestrator object.
        """
        pass

    def handle_message(self, user_message: str, language: str, chat_history: List[dict], conversation_id: str , orchestrator: OrchestrationSettings,
                       global_index_name: str, user_index_name: str, config: dict, **kwargs: dict) -> dict:
        orchestrator = get_orchestrator(orchestrator.strategy.value, language,global_index_name, user_index_name)
        if orchestrator is None:
            raise ValueError(f"Unknown orchestration strategy: {orchestrator.strategy.value}")
        return orchestrator.handle_message(user_message,chat_history, conversation_id, config)

    def extract_followupquestions(self, answer: str) -> Tuple[str, list]:
        followuptag = answer.find('Follow-up Questions')
        followupquestions = answer.find('<<')

        followuptag = min(followuptag, followupquestions) if followuptag != -1 and followupquestions != -1 else max(followuptag, followupquestions)
        answer_without_followupquestions = answer[:followuptag] if followuptag != -1 else answer
        followup_questions = answer[followuptag:].strip() if followuptag != -1 else ''

        pattern = r'\<\<(.*?)\>\>'
        match = re.search(pattern, followup_questions)
        followup_questions_list = []
        while match:
            followup_questions_list.append(followup_questions[match.start()+2:match.end()-2])
            followup_questions = followup_questions[match.end():]
            match = re.search(pattern, followup_questions)

        if followup_questions_list:
            pattern = r'\d. (.*)'
            match = re.search(pattern, followup_questions)
            while match:
                followup_questions_list.append(followup_questions[match.start()+3:match.end()])
                followup_questions = followup_questions[match.end():]
                match = re.search(pattern, followup_questions)

        if followup_questions_list:
            pattern = r'Follow-up Question: (.*)'
            match = re.search(pattern, followup_questions)
            while match:
                followup_questions_list.append(followup_questions[match.start()+19:match.end()])
                followup_questions = followup_questions[match.end():]
                match = re.search(pattern, followup_questions)

        followuptag = answer_without_followupquestions.lower().find('follow-up questions')
        if followuptag != -1:
            answer_without_followupquestions = answer_without_followupquestions[:followuptag]
        followuptag = answer_without_followupquestions.lower().find('follow up questions')
        if followuptag != -1:
            answer_without_followupquestions = answer_without_followupquestions[:followuptag]

        return answer_without_followupquestions, followup_questions_list
