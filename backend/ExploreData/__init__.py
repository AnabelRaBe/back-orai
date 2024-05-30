import os
import json
from dotenv import load_dotenv
from ..utilities.helpers.ExploreDataHelper import ExploreData
import logging
import azure.functions as func
import urllib.parse
import requests

def process_explore_data(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Requested to start processing ExploreData')

    exploredata = ExploreData()

    load_dotenv()
    explored_index = os.getenv("AZURE_INGEST_INDEX")
    container_name = os.getenv("AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME")

    data = req.get_json()
    access_token = data['access_token']
    token_id = data['token_id']
    groups_access = [os.getenv("ORAI_ADMIN_USER_GROUP_NAME"), os.getenv("ORAI_ADVANCE_USER_GROUP_NAME")]

    params = {"token_id": token_id,
              "access_token": access_token,
              "groups_access": groups_access}

    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")

    try:
        response = requests.post(backend_url, json=params)

        if response.status_code == 200:
            index_metadata = exploredata.get_index_metadata(explored_index)
            blob_metadata = exploredata.get_blob_metadata(container_name)
            merged_metadata = exploredata.merge_metadata(index_metadata, blob_metadata)

            json_data = json.dumps(merged_metadata, indent=2)
            return func.HttpResponse(json_data, status_code=200, mimetype="application/json")

        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code=response.status_code)

    except Exception as e:
        logging.exception(f"Response failed: {e}")
        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")

main = process_explore_data