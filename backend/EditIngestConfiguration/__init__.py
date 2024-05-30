"""
Module for editing the ingest configuration.
This module provides functionality to handle requests for editing the ingest configuration.
"""
import logging
import json
import os
import urllib.parse
import requests
import azure.functions as func
from ..utilities.helpers.ConfigHelper import ConfigHelper
from dotenv import load_dotenv


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Function to handle requests for editing the ingest configuration.
    This function receives an HTTP request containing the access token, token ID, and document processors to be edited in the ingest configuration. It verifies the user's authentication, then edits the ingest configuration accordingly and sends back a response indicating success or failure.
    Args:
        req (func.HttpRequest): The HTTP request object containing the access token, token ID, and document processors.
    Returns:
        func.HttpResponse: An HTTP response indicating success or failure of the operation.
    """
    logging.info('Requested to start editing the ingest configuration.')

    load_dotenv()

    CONFIG_CONTAINER_NAME = "config"

    data = req.get_json()
    access_token = data['access_token'] 
    token_id = data['token_id']
    document_processors = data['document_processors']

    groups_access = [os.getenv("ORAI_ADMIN_USER_GROUP_NAME"), os.getenv("ORAI_ADVANCE_USER_GROUP_NAME")]

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}

    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")

    try:
        response = requests.post(backend_url, json=params)
        if response.status_code == 200:
            try:
                ConfigHelper.edit_ingest_config_as_active(document_processors)

                response_message = {"Success": "Configuration saved successfully!"}
                return func.HttpResponse(json.dumps(response_message), status_code=200)
            except Exception as e:
                error_message = {"error": str(e)}
                return func.HttpResponse(json.dumps(error_message), status_code=500)
 
    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")