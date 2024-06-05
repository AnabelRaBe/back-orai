"""
This module is responsible for saving conversations in a PostgreSQL database.
"""
import logging
import datetime
import json, os, requests
import azure.functions as func
from ..utilities.tools.GenerateTopicTool import GenerateTopicTool
from ..utilities.common.PostgreSQL import PostgreSQL
from ..utilities.common.ValidationRequest import RequestSave
from dotenv import load_dotenv
import urllib.parse

def set_user(rows, postgresql, request_body, timestamptz):
    """
    Sets the user information in the database.
    Args:
        rows (list): The list of rows returned from a database query.
        postgresql (object): The PostgreSQL object used for database operations.
        request_body (object): The request body containing user information.
        timestamptz (str): The timestamp with timezone.
    Returns:
        object: The PostgreSQL object.
    """
    if not rows:
        user = postgresql.select_data("users", f"user_id = '{request_body.user_id}'")
        if not user:
            postgresql.insert_data("users", f"'{request_body.user_id}', '{request_body.user_name}', '{timestamptz}'", "(user_id, username, created_at)")
        postgresql.insert_data("conversations", f"'{request_body.conversation_id}', '{request_body.user_id}', '{request_body.save_chat}', '{request_body.language}', '{timestamptz}', '{timestamptz}'", "(conversation_id, user_id, save_chat, language, created_at, modified_at)")
    return postgresql

def set_message(request_body, postgresql, timestamptz):
    """
    Inserts messages into the database and updates the conversation's modified_at timestamp.
    Args:
        request_body (object): The request body containing the conversation and message details.
        postgresql (object): The PostgreSQL database object.
        timestamptz (str): The timestamp with timezone.
    Returns:
        object: The updated PostgreSQL database object.
    """
    if request_body.message:
        for message in request_body.message:
            message_str = json.dumps(message)
            message_str = message_str.replace("'", "''")
            id_message = postgresql.get_max_id_by_conversation_id("messages", request_body.conversation_id) + 1
            postgresql.insert_data("messages", f"'{request_body.conversation_id}', {id_message}, '{message_str}', '{timestamptz}'", "(conversation_id, id_message, message_text, created_at)")
        postgresql.update_data("conversations", f"modified_at = '{timestamptz}'", f"conversation_id = '{request_body.conversation_id}' AND user_id = '{request_body.user_id}'")
    return postgresql

def set_topic(request_body, rows, postgresql, timestamptz):
    """
    Sets the topic for a conversation based on the chat history and other parameters.
    Args:
        request_body (object): The request body containing the conversation ID, user ID, and other details.
        rows (list): The rows retrieved from the database.
        postgresql (object): The PostgreSQL object used for database operations.
        timestamptz (str): The timestamp with time zone.
    Returns:
        object: The updated PostgreSQL object.
    """
    if (request_body.save_chat or len(rows) > 0 and rows[0][0]) and len(rows) > 0 and rows[0][2] is None: 
        history_query = postgresql.select_data("messages", f"conversation_id = '{request_body.conversation_id}'", 'message_text')
        history = [list(tupla) for tupla in history_query]
        if history:
            generate_topic_tools = GenerateTopicTool()
            topic = generate_topic_tools.generate_topic(history, rows[0][1])
            topic = topic.replace("'", "''")
            postgresql.update_data("conversations", f"topic = '{topic}', save_chat = '{request_body.save_chat}', modified_at = '{timestamptz}'", f"conversation_id = '{request_body.conversation_id}' AND user_id = '{request_body.user_id}'")
    return postgresql

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Saves a conversation in a PostgreSQL database.
    Args:
        req (func.HttpRequest): The HTTP request object.
    Returns:
        func.HttpResponse: The HTTP response object.
    """
    logging.info('Request saves conversation in a PostgreSQL database')

    load_dotenv()

    try:
        request_body = RequestSave(**req.get_json())
        
        access_token = request_body.access_token
        token_id = request_body.token_id
        groups_access = [os.getenv("GROUP_NAME")]

        params = {"token_id": token_id,
                "access_token": access_token,
                "groups_access": groups_access}

        backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:
            try:
                now = datetime.datetime.now()
                timestamptz = now.isoformat()
                postgresql = PostgreSQL()

                rows = postgresql.select_data("conversations", f"conversation_id = '{request_body.conversation_id}' AND user_id = '{request_body.user_id}'", 'save_chat, language, topic')

                postgresql = set_user(rows, postgresql, request_body, timestamptz)

                postgresql = set_message(request_body, postgresql, timestamptz)

                postgresql = set_topic(request_body, rows, postgresql, timestamptz)

                postgresql.close_connection()

                return func.HttpResponse(status_code=204)

            except Exception as e:
                logging.exception("Exception in SaveConversation")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 

        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 
