"""
Module for handling conversation deletion requests.
This module provides functions to process requests for deleting conversations and their associated messages.
"""
import logging
import json, requests
import azure.functions as func
from ..utilities.common.PostgreSQL import PostgreSQL
from ..utilities.common.ValidationRequest import RequestDelete
from dotenv import load_dotenv
import urllib.parse, os

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Entry function handling the conversation deletion request.
    Parameters:
        req (func.HttpRequest): The received HTTP request.
    Returns:
        func.HttpResponse: The resulting HTTP response.
    """
    logging.info('Requested to delete conversation')

    load_dotenv()

    try:
        request_body = req.get_json()

        validated_body = RequestDelete(**request_body)

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
                save_chat = postgresql.select_data("conversations", f"conversation_id = '{validated_body.conversation_id}'", 'save_chat')

                if validated_body.delete or (not validated_body.delete and not save_chat[0][0]):
                    postgresql.delete_data("conversations", f"conversation_id = '{validated_body.conversation_id}'")
                    postgresql.delete_data("message_store", f"session_id = '{validated_body.conversation_id}'")

                postgresql.close_connection()

                return func.HttpResponse(status_code=204)

            except Exception as e:
                logging.exception("Exception in DeleteConversation")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 
        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json") 
