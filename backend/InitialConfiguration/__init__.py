"""
This endpoint grabs the configuration json from the active.json file found in the Azure "config" container.
"""

import logging
import json
import os
import urllib.parse
import requests
import azure.functions as func
from ..utilities.helpers.AzureBlobStorageHelper import AzureBlobStorageClient
from dotenv import load_dotenv


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Gets the configuration json from the active.json file located in the Azure "config" container.
    Parameters:
        func.HttpResponse
    Returns:
        func.HttpResponse
    """
    logging.info('Requested to start processing InitialConfiguration')

    load_dotenv()

    config_container_name = "config"

    data = req.get_json()
    access_token = data['access_token'] 
    token_id = data['token_id']

    groups_access = [os.getenv("GROUP_NAME")]

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}

    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")

    application_json = "application/json"

    try:
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:
            try: 
                blob_client = AzureBlobStorageClient(container_name=config_container_name)
                config = blob_client.download_file("active.json")
                return func.HttpResponse(config, status_code=200, mimetype=application_json)
            except Exception as e:
                logging.exception("Exception in InitialConfiguration")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype=application_json)
        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as e:
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype=application_json)
