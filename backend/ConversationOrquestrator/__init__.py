"""
This module is responsible for processing conversations using the langchain orchestrator.
It receives an HTTP request containing chat history, language, user index name, access token, and token ID.
It then uses the Orchestrator, ConfigHelper, and Hyperlinks classes from the utilities.helpers module to handle the conversation.
The processed messages are returned as an HTTP response.
"""
import os
import json
import logging
import urllib.parse
import azure.functions as func
import requests
from dotenv import load_dotenv
from ..utilities.helpers.OrchestratorHelper import Orchestrator
from ..utilities.helpers.ConfigHelper import ConfigHelper
from ..utilities.helpers.HyperlinksHelper import Hyperlinks

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process the conversation using langchain orchestrator.
    Args:
        req (func.HttpRequest): The HTTP request object.
    Returns:
        func.HttpResponse: The HTTP response object.
    """
    logging.info('Requested to start processing the conversation using langchain orchestrator')
    
    load_dotenv()

    config = ConfigHelper.get_active_config_or_default()
    
    data = req.get_json()
    request = data['chat_history']
    language = data['language']
    user_index_name = data['user_index_name']
    
    access_token = data['access_token'] 
    token_id = data['token_id']
    groups_access = [os.getenv("GROUP_NAME")]

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}
    
    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")
    
    message_orchestrator = Orchestrator()
    hyperlinks = Hyperlinks()

    application_json = "application/json"

    try:
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:
            
            try:
                user_message = request["messages"][-1]['content']
                conversation_id = request["conversation_id"]
                user_assistent_messages = list(filter(lambda x: x['role'] in ('user', 'assistant'), request["messages"][0:-1]))  
                chat_history = get_chat_history(user_assistent_messages)
                messages = message_orchestrator.handle_message(user_message=user_message, language = language,chat_history=chat_history,
                                                            conversation_id=conversation_id, orchestrator=config.orchestrator,
                                                            global_index_name=os.getenv("AZURE_SEARCH_INDEX"), user_index_name=user_index_name, config=config)

                chat_followup_questions_list = []
                for message in messages:
                    if message["role"] == "assistant":
                        answer_without_followup, chat_followup_questions_list = message_orchestrator.extract_followupquestions(message["content"])
                        message["content"] = answer_without_followup

                response = create_response(messages, chat_followup_questions_list, os.getenv("AZURE_OPENAI_MODEL"))
                answer_with_hyperlinks = hyperlinks.add_hyperlinks(response, answer_without_followup)
                user_message = user_message.replace("'", "").replace('"', '')
                answer_with_hyperlinks = answer_with_hyperlinks.replace("'", "").replace('"', '')
                params = create_params(conversation_id, user_index_name, user_message, answer_with_hyperlinks, language, access_token, token_id)
                save_chat_temp_url = urllib.parse.urljoin(os.getenv('BACKEND_URL', 'http://localhost:7071'), "/api/SaveConversation")
                requests.post(save_chat_temp_url, json=params)

                for message in messages:
                    if message["role"] == "assistant":
                        message["content"] = answer_with_hyperlinks
               
                response = create_response(messages, chat_followup_questions_list, os.getenv("AZURE_OPENAI_MODEL"))

                return func.HttpResponse(json.dumps(response), status_code=200, mimetype=application_json) 
            
            except Exception as e:
                logging.exception("Exception in langchain orchestrator")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype=application_json) 
        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype=application_json) 

def get_chat_history(user_assistent_messages):
    """
    Extracts the chat history from the user and assistant messages.
    Args:
        user_assistent_messages (list): List of user and assistant messages.
    Returns:
        list: List of chat history tuples.
    """
    chat_history = []
    for i, k in enumerate(user_assistent_messages):
        if i % 2 == 0:
            chat_history.append((user_assistent_messages[i]['content'], user_assistent_messages[i+1]['content']))
    return chat_history

def create_response(messages, chat_followup_questions_list, azure_openai_model):
    """
    Creates the response object.
    Args:
        messages (list): List of messages.
        chat_followup_questions_list (list): List of follow-up questions.
        azure_openai_model (str): Azure OpenAI model.
    Returns:
        dict: The response object.
    """
    response = {
        "id": "response.id",
        "model": azure_openai_model,
        "created": "response.created",
        "object": "response.object",
        "choices": [
            {
                "messages": messages,
                "followupquestions": chat_followup_questions_list
            }
        ]
    }
    return response

def create_params(conversation_id, user_index_name, user_message, answer_with_hyperlinks, language, access_token, token_id):
    """
    Creates the parameters for saving the conversation.
    Args:
        conversation_id (str): Conversation ID.
        user_index_name (str): User index name.
        user_message (str): User message.
        answer_with_hyperlinks (str): Answer with hyperlinks.
        language (str): Language.
        access_token (str): Access token.
        token_id (str): Token ID.
    Returns:
        dict: The parameters for saving the conversation.
    """
    params = {
        "conversation_id": conversation_id,
        "user_id": user_index_name.replace("-index", ""),
        "message": [
            {
                "author": "human",
                "content": user_message,
            },
            {
                "author": "ai",
                "content": answer_with_hyperlinks,
            }
        ],
        "language": language,
        "access_token": access_token,
        "token_id": token_id
    }
    return params
