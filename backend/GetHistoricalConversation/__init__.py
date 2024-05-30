"""
Azure Function script to handle HTTP requests for retrieving historical messages of a conversation.
"""
import logging
import json, os, requests
import azure.functions as func
from ..utilities.common.PostgreSQL import PostgreSQL
from ..utilities.common.ValidationRequest import RequestHistoricalMessage, Message
from dotenv import load_dotenv
import urllib.parse

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Handles HTTP requests to retrieve historical messages of a conversation.
    Args:
        req (func.HttpRequest): The HTTP request object.
    Returns:
        func.HttpResponse: The HTTP response object containing the historical messages data.
    Raises:
        Exception: If there is an error during the process.
    """

    logging.info('Requested to get historical messages')

    load_dotenv()

    try:

        request_body = req.get_json()
        
        conversation_id = request_body["conversation_id"]
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

                messages = postgresql.select_data("messages", f"conversation_id = '{conversation_id}' ORDER BY id_message ASC",
                                                'id_message, message_text, created_at')

                messages_json = RequestHistoricalMessage(
                    messages=[
                        Message(
                            id=tupla[0],
                            author=tupla[1]['author'],
                            content=tupla[1]['content'],
                            datetime=tupla[2].isoformat()
                        ) for tupla in messages
                    ]
                )

                postgresql.close_connection()
                return func.HttpResponse(body=messages_json.model_dump_json(), status_code=200)

            except Exception as e:
                logging.exception("Exception in GetHistoricalConversation")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 

        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 


