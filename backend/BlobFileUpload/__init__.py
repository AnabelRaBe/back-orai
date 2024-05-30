"""
This endpoint processes file uploads to the Azure storage account.
"""

import os
import json
import logging
import azure.functions as func
import requests
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from ..utilities.helpers.AzureBlobStorageHelper import AzureBlobStorageClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    The upload of files to the Azure storage account is processed.
    Params:
        func.HttpResponse
    Returns:
        func.HttpResponse
    """
    logging.info('Requested to start processing the blob file upload.')

    load_dotenv()

    access_token = req.form.get('access_token')
    token_id = req.form.get('token_id')
    user_id = req.form.get('user_id')
    file_name = req.form.get('file_name')
    file_bytes = req.files['file'].read()

    chunking_strategy = req.form.get('chunking_strategy')
    chunking_size = req.form.get('chunking_size')
    chunking_overlap = req.form.get('chunking_overlap')
    loading_strategy = req.form.get('loading_strategy')
    user_name = urllib.parse.quote(req.form.get('user_name'))

    file_extension = file_name.split(".")[-1]
    file_size_kb = str(round(len(file_bytes)/1024,2))
    upload_date = str(datetime.now().strftime("%d/%m/%Y"))

    is_global_index_str = req.form.get('is_global_index', '').lower()
    is_global_index = is_global_index_str == 'true' if is_global_index_str else False

    if is_global_index:
        container_name = os.getenv("AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME")
        groups_access = [os.getenv("ORAI_ADMIN_USER_GROUP_NAME"), os.getenv("ORAI_ADVANCE_USER_GROUP_NAME")]
    else:
        file_name = f"{user_id}/{file_name}"
        container_name = os.getenv("AZURE_BLOB_LOCAL_DOCUMENTS_CONTAINER_NAME")
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
                blob_storage_client = AzureBlobStorageClient(container_name = container_name)
                blob_storage_client.upload_blob_file(bytes_data = file_bytes, uploaded_file_name = file_name, user_id = user_id)

                if is_global_index:
                    blob_storage_client.upsert_blob_metadata(file_name, {
                                                                        'upload_date': upload_date,
                                                                        'file_extension':file_extension,
                                                                        'file_size_kb':file_size_kb,
                                                                        'chunking_strategy': chunking_strategy,
                                                                        'chunking_size': chunking_size,
                                                                        'chunking_overlap': chunking_overlap,
                                                                        'loading_strategy': loading_strategy,
                                                                        'user_name': user_name})

                logging.info(f"The file {file_name} has been uploaded.")
                return func.HttpResponse(json.dumps({"Success": f"The file {file_name} has been uploaded."}), status_code=200, mimetype=application_json)
            except Exception as e:
                logging.exception("Exception in BlobFileUpload")
                return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype=application_json)
        else:
            logging.info(f'Authentication error: {response.json()}. status_code: {response.status_code}')
            return func.HttpResponse(json.dumps(response.json()), status_code = response.status_code)

    except Exception as ex:
        logging.exception(f"Response failed: {ex}")
        return func.HttpResponse(json.dumps({"Error": str(ex)}), status_code=500, mimetype=application_json)
        return func.HttpResponse(json.dumps({"Error": str(ex)}), status_code=500, mimetype=application_json)
