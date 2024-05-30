"""
This module update topic of the conversation.
"""
import logging
import datetime
import json, os, requests
import azure.functions as func
from ..utilities.common.PostgreSQL import PostgreSQL
from ..utilities.common.ValidationRequest import RequestUpdateTopic
from dotenv import load_dotenv
import urllib.parse


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Update the topic of the conversation.
    This function handles HTTP requests to update the topic of a conversation. It validates the request, 
    checks authentication with the backend, and updates the topic in the database if authentication is successful.
    Args:
        req (func.HttpRequest): The HTTP request object containing the request body.
    Returns:
        func.HttpResponse: The HTTP response object indicating the success or failure of the request.
    Raises:
        Exception: If there is an error processing the request or updating the topic in the database.
    """
    logging.info('Python HTTP trigger function processed a request.')

    load_dotenv()

    try:
        request_body = req.get_json()

        validated_body = RequestUpdateTopic(**request_body)
        access_token = validated_body.access_token
        token_id = validated_body.token_id
        groups_access = [os.getenv("GROUP_NAME")]
        params = {"token_id": token_id,
                "access_token": access_token,
                "groups_access": groups_access}
        backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:
            try:
                postgresql = PostgreSQL()
                now = datetime.datetime.now()
                timestamptz = now.isoformat()

                postgresql.update_data("conversations", f"topic = '{validated_body.topic}', modified_at = '{timestamptz}'",
                                        f"conversation_id = '{validated_body.conversation_id}' AND user_id = '{validated_body.user_id}'")
                
                postgresql.close_connection()
                return func.HttpResponse(status_code=204)
            
            except Exception as e:
                logging.exception("Exception in UpdateTopicConversation")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 

        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")