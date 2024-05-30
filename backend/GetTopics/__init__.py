"""
Module for handling HTTP requests to retrieve topics from conversations.
"""
import logging
import json, os, requests
import azure.functions as func
from ..utilities.common.PostgreSQL import PostgreSQL
from ..utilities.common.ValidationRequest import RequestTopic
from dotenv import load_dotenv
import urllib.parse


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handles HTTP requests to retrieve topics from conversations.
    Args:
        req (func.HttpRequest): The HTTP request object.
    Returns:
        func.HttpResponse: The HTTP response object containing the topics data.
    Raises:
        Exception: If there is an error during the process.
    """

    logging.info('Requested to get topics from conversations')

    load_dotenv()

    try:
        request_body = req.get_json()

        user_id = request_body["user_id"].replace("-index", "")
        access_token = request_body['access_token']
        token_id = request_body['token_id']
        groups_access = [os.getenv("GROUP_NAME")]

        params = {"token_id": token_id,
                "access_token": access_token,
                "groups_access": groups_access}

        backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:

            try:
                postgresql = PostgreSQL()

                topics = postgresql.select_data("conversations", f"user_id = '{user_id}' AND save_chat = 'True' AND topic IS NOT NULL ORDER BY modified_at ASC",
                                                'conversation_id, topic, created_at, modified_at')
                topic_json = [
                    {
                        "conversation_id": str(tupla[0]),
                        "topic": tupla[1],
                        "created_at": str(tupla[2]),
                        "modified_at": str(tupla[3])
                    }
                    for tupla in topics
                    if RequestTopic(conversation_id=tupla[0], topic=tupla[1], created_at=tupla[2], modified_at=tupla[3])
                ]
                
                postgresql.close_connection()
                return func.HttpResponse(body=json.dumps(topic_json), status_code=200)
            
            except Exception as e:
                logging.exception(f"Exception in GetTopics: {e}")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 

        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 


