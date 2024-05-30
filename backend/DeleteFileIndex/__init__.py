"""
This module provides functions for deleting files from an Azure search index and an Azure blob storage container.
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
from ..utilities.helpers.AzureBlobStorageHelper import AzureBlobStorageClient
from ..utilities.helpers.AzureSearchHelper import AzureSearchHelper

def get_files(search_client):
    """
    Retrieves files from the search index.
    Parameters:
        search_client: The Azure search client.
    Returns:
        dict: Dictionary containing the files retrieved from the search index.
    """
    return search_client.search("*", select="id, title", include_total_count=True)

def set_selected_files(files_names, file_options):
    """
    Selects files to delete based on provided file names and options.
    Parameters:
        files_names (list): List of file names.
        file_options (list): List of file options.
    Returns:
        dict: Dictionary containing the selected files to delete.
    """
    selected_files = {}
    for file_name in files_names:
        for file_option_name in file_options:
            if file_name in file_option_name:
                selected_files[file_option_name] = ""

    return selected_files

def output_results(results, files_names):
    """
    Processes search results and selects files to delete.
    Parameters:
        results (dict): Dictionary containing the search results.
        files_names (list): List of file names.
    Returns:
        dict: Dictionary containing the selected files to delete.
    """
    files = {}
    if results.get_count() == 0:
        logging.error("No files available.")
        return []
    else:
        for result in results:
            id = result['id']
            filename = result['title']
            if filename in files:
                files[filename].append(id)
            else:
                files[filename] = [id]

        file_options = [f"{i + 1}. {filename}" for i, filename in enumerate(files.keys())]
        logging.info(f"**Total indexed files: {file_options}**")

        selected_files = set_selected_files(files_names, file_options)

        logging.info(f"**Selected files: {selected_files}**")

        files_to_delete = {filename.split(". ", 1)[1]: files[filename.split(". ", 1)[1]] for filename in selected_files}
        return files_to_delete

def delete_files_in_index(files, search_client):
    """
    Deletes files from the search index.
    Parameters:
        files (dict): Dictionary containing the files to delete.
        search_client: The Azure search client.
    """
    ids_to_delete = []
    files_to_delete = []

    for filename, ids in files.items():

        files_to_delete.append(filename)
        ids_to_delete += [{'id': id} for id in ids]

    if len(ids_to_delete) == 0:
        logging.exception("No files selected")

    search_client.delete_documents(ids_to_delete)

    logging.info('Deleted files: ' + str(files_to_delete))

def delete_files_in_blob_storage(files_names, azure_blob_storage_client):
    """
    Deletes files from Azure blob storage.
    Parameters:
        files_names (list): List of file names.
        azure_blob_storage_client: The Azure Blob Storage client.
    """
    for file_name in files_names:
        azure_blob_storage_client.delete_file(file_name)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Entry function handling the file deletion request.
    Parameters:
        req (func.HttpRequest): The received HTTP request.
    Returns:
        func.HttpResponse: The resulting HTTP response.
    """
    logging.info('Requested to delete files.')
    load_dotenv()

    data = req.get_json()
    files_names = data['files_names']
    access_token = data['access_token']
    token_id = data['token_id']

    logging.info(f"Input: {data}")

    groups_access = [os.getenv("ORAI_ADMIN_USER_GROUP_NAME"), os.getenv("ORAI_ADVANCE_USER_GROUP_NAME")]
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    container_name = os.getenv("AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME")

    params = {"token_id": token_id,
            "access_token": access_token,
            "groups_access": groups_access}

    backend_url = urllib.parse.urljoin(os.getenv('BACKEND_URL'), "/api/Authentication")

    application_json = "application/json"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(backend_url, json=params) as response:

                if response.status == 200:
                    try:
                        azure_blob_storage_client = AzureBlobStorageClient(container_name=container_name)
                        vector_store_helper: AzureSearchHelper = AzureSearchHelper(index_name=index_name)
                        search_client = vector_store_helper.get_vector_store().client

                        # Delete files in index
                        results = get_files(search_client)
                        files_to_delete = output_results(results, files_names)
                        delete_files_in_index(files_to_delete, search_client)
                        logging.info(f"Deleted {files_to_delete} in the index {index_name}")

                        # Delete files in blob storage
                        delete_files_in_blob_storage(files_names, azure_blob_storage_client)
                        logging.info(f"Deleted {files_names} in the blob storage container {container_name}")

                        return func.HttpResponse(json.dumps({"Success": f"Deleted: {files_names}."}), status_code=200)

                    except Exception as e:
                        logging.exception("Exception in DeleteIndexFile")
                        return func.HttpResponse(json.dumps({"Error": str(e)}), status_code=500, mimetype=application_json)

                else:
                    logging.info(f'Authentication error: {response.json()}. status_code: {response.status}')
                    return func.HttpResponse(json.dumps(response.json()), status_code = response.status, mimetype=application_json)
                
        except Exception as ex:
            logging.exception(f"Response failed: {ex}")
            return func.HttpResponse(json.dumps({"Error": str(ex)}), status_code=500, mimetype=application_json)