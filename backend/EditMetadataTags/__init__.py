"""
Module for handling HTTP requests to start editing the tags options in the ingest process.
This module contains the `main` function, an Azure Function triggered by an HTTP request. It receives a POST request containing data including an access token, token ID, and tags to be edited. It then edits the tags options as active in the configuration using `ConfigHelper`.
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
    Args:
    req (func.HttpRequest): The HTTP request object.
    Returns:
    func.HttpResponse: The HTTP response containing a success message if the tags are saved successfully, or an error message if there's an exception.
    """
    logging.info('Requested to start editing the tags options in ingest process.')

    load_dotenv()

    data = req.get_json()
    access_token = data["access_token"]
    token_id = data["token_id"]
    tags = data["tags"]

    groups_access = [os.getenv("ORAI_ADMIN_USER_GROUP_NAME"), os.getenv("ORAI_ADVANCE_USER_GROUP_NAME")]

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}

    backend_url = urllib.parse.urljoin(os.getenv("BACKEND_URL"), "/api/Authentication")

    try:
        response = requests.post(backend_url, json=params)
        if response.status_code == 200:
            try:
                ConfigHelper.edit_tags_options_as_active(tags)

                response_message = {"Success": "New tags saved successfully!"}
                return func.HttpResponse(json.dumps(response_message), status_code=200)
            except Exception as e:
                error_message = {"error": str(e)}
                return func.HttpResponse(json.dumps(error_message), status_code=500)
   
    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")