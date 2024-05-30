"""
This endpoint is the predecessor to ingesting documents into the index. Documents are prepared to be passed to BatchPushResults.
"""
import os
import json
import asyncio
import logging
import requests
import urllib.parse
import aiohttp
import azure.functions as func
from dotenv import load_dotenv
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from ..utilities.helpers.AzureBlobStorageHelper import AzureBlobStorageClient

def search_metadata_by_file_name(filename:str, list_metadata:list) -> str: 
    """
    Search metadata by file name.
    Parameters:
        filename (str): The name.
        metadata_list (list): List of dicts with filename and metadata.
    Returns:
        json.dumps(metadata)
    """
    metadata = {}

    for file in list_metadata:
        keys = list(file.keys())
        if keys[0] == filename:
            metadata = file[filename]

    return json.dumps(metadata)

def add_user_id_in_metadata_key(user_id, metadata_list):
    """
    Add user_id in metadata key.
    Parameters:
        user_id (str): The user_id.
        metadata_list (list): List of dicts with filename and metadata.
    Returns:
        metadata_list
    """
    for metadata in metadata_list:
        for key in list(metadata.keys()):
            new_key = f"{user_id}/{key}"
            metadata[new_key] = metadata.pop(key)
    return metadata_list

def set_variables_values(is_global_index, user_id, metadata):
    """
    Set variables values.
    Parameters:
        is_global_index (bool): Must the document be indexed in the global index or not?
        user_id (str): The user_id.
        metadata_list (list): List of dicts with filename and metadata.
    Returns:
        index_name (str): The index name.
        container_name (str): The container name.
        groups_access (list of str): The list of the groups that can use the endpoints. 
        metadata (list of dict): The list of metadata.
    """
    if is_global_index:
        index_name = os.getenv("AZURE_SEARCH_INDEX")
        container_name = os.getenv("AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME")
        groups_access = [os.getenv("ORAI_ADMIN_USER_GROUP_NAME"), os.getenv("ORAI_ADVANCE_USER_GROUP_NAME")] 
    else:
        index_name = f"{user_id}-index" 
        container_name = os.getenv("AZURE_BLOB_LOCAL_DOCUMENTS_CONTAINER_NAME")
        groups_access = [os.getenv("GROUP_NAME")]
        metadata = add_user_id_in_metadata_key(user_id, metadata)

    return index_name, container_name, groups_access, metadata 

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Start processing all documents received.
    Returns: func.HttpResponse()
    """
    logging.info('Requested to start processing all documents received.')
    
    load_dotenv()

    data = req.get_json()
    user_id = data['user_id']
    is_global_index = data['is_global_index']
    process_all = data['process_all']
    access_token = data['access_token']
    token_id = data['token_id']
    metadata = data['metadata']

    logging.info(f"Input: {data}")

    index_name, container_name, groups_access, metadata = set_variables_values(is_global_index, user_id, metadata)

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}
    
    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(backend_url, json=params) as response:

                if response.status == 200:
                    try:
                        azure_blob_storage_client = AzureBlobStorageClient(container_name=container_name)

                        files_data = azure_blob_storage_client.get_all_files()
                        files_data = list(filter(lambda x : not x['embeddings_added'], files_data)) if process_all != True else files_data
                        files_data = list(map(lambda x: {'filename': x['filename'],
                                                        'index_name': index_name,
                                                        'metadata': search_metadata_by_file_name(x['filename'], metadata),
                                                        'container_name': container_name}, files_data))
                        if files_data:
                            producer = EventHubProducerClient.from_connection_string(
                                conn_str=os.getenv('EVENT_HUB_CONNECTION_STR'),
                                eventhub_name=os.getenv('EVENT_HUB_NAME')
                            )
                            async with producer:
                                event_data_batch = await producer.create_batch()
                                for fd in files_data:
                                    event_data_batch.add(EventData(json.dumps(fd).encode('utf-8')))
                                await producer.send_batch(event_data_batch)
                        
                        files_names = []
                        for file_data in files_data:
                            files_names.append(file_data['filename'])
                        logging.info(f"Processed files: {files_names}")

                        return func.HttpResponse(json.dumps({"Success": f"Conversion started successfully for {len(files_data)} documents."}), status_code=200)

                    except Exception as e:
                        logging.exception("Exception in BatchStartProcessing")
                        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype="application/json")

                else:
                    logging.info(f'Authentication error: {response.json()}. status_code: {response.status}')
                    return func.HttpResponse(json.dumps(response.json()), status_code = response.status)
            
        except Exception as ex:
            logging.exception(f"Response failed: {ex}")
            return func.HttpResponse(json.dumps({"Error": str(ex)}), status_code=500, mimetype="application/json")