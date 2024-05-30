"""
This code is responsible for interacting with Azure Blob Storage.
It provides functionalities to upload, download, and delete files from the storage.
It also includes methods to retrieve metadata and generate shared access signatures (SAS) for containers and blobs.
"""

import os
import json
import mimetypes
import chardet
from os import remove
from typing import Optional
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, generate_container_sas, ContentSettings
from .EnvHelper import EnvHelper

class AzureBlobStorageClient:
    """
    A client class for interacting with Azure Blob Storage.
    Args:
        account_name (Optional[str]): The name of the Azure Blob Storage account. If not provided, it will be fetched from the environment variable AZURE_BLOB_ACCOUNT_NAME.
        account_key (Optional[str]): The access key for the Azure Blob Storage account. If not provided, it will be fetched from the environment variable AZURE_BLOB_ACCOUNT_KEY.
        container_name (Optional[str]): The name of the container in Azure Blob Storage. If not provided, it will be fetched from the environment variable AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME.
    Attributes:
        account_name (str): The name of the Azure Blob Storage account.
        account_key (str): The access key for the Azure Blob Storage account.
        connect_str (str): The connection string for the Azure Blob Storage account.
        container_name (str): The name of the container in Azure Blob Storage.
        blob_service_client (BlobServiceClient): The client object for interacting with the Azure Blob Storage service.
    """

    def __init__(self, account_name: Optional[str] = None, account_key: Optional[str] = None, container_name: Optional[str] = None):
        """
        Initializes a new instance of the AzureBlobStorageClient class.
        Args:
            account_name (Optional[str]): The name of the Azure Blob Storage account. If not provided, it will be fetched from the environment variable AZURE_BLOB_ACCOUNT_NAME.
            account_key (Optional[str]): The access key for the Azure Blob Storage account. If not provided, it will be fetched from the environment variable AZURE_BLOB_ACCOUNT_KEY.
            container_name (Optional[str]): The name of the container in Azure Blob Storage. If not provided, it will be fetched from the environment variable AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME.
        """
        env_helper : EnvHelper = EnvHelper()

        self.account_name = account_name if account_name else env_helper.AZURE_BLOB_ACCOUNT_NAME
        self.account_key = account_key if account_key else env_helper.AZURE_BLOB_ACCOUNT_KEY
        self.connect_str = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
        self.container_name : str = container_name if container_name else env_helper.AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME
        self.blob_service_client : BlobServiceClient = BlobServiceClient.from_connection_string(self.connect_str)

    def upload_file(self, bytes_data, file_name, content_type='application/pdf'):
        """
        Uploads a file to Azure Blob Storage.
        Args:
            bytes_data (bytes): The file data to be uploaded.
            file_name (str): The name of the file.
            content_type (str, optional): The content type of the file. Defaults to 'application/pdf'.
        Returns:
            str: The URL of the uploaded file with a generated SAS token.
        """
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        blob_client.upload_blob(bytes_data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        return blob_client.url + '?' + generate_blob_sas(self.account_name, self.container_name, file_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))

    def download_file(self, file_name):
        """
        Downloads a file from Azure Blob Storage.
        Args:
            file_name (str): The name of the file to download.
        Returns:
            bytes: The content of the downloaded file.
        """
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        return blob_client.download_blob().readall()

    def delete_file(self, file_name):
        """
        Deletes a file from the Azure Blob Storage container.
        Args:
            file_name (str): The name of the file to be deleted.
        Returns:
            None
        """
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)
        blob_client.delete_blob()

    def get_all_files_feedback(self, container_name: str) -> list:
        """
        Retrieves all files from the specified container in Azure Blob Storage and returns a list of feedbacks.
        Args:
            container_name (str): The name of the container in Azure Blob Storage.
        Returns:
            list: A list of feedbacks, where each feedback is a dictionary parsed from the downloaded file.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        feedbacks = []
        for blob in blob_list:
            feedback = self.download_file(blob.name)
            feedbacks.append(json.loads(feedback))

        return feedbacks

    def get_all_files(self):
        """
        Retrieves a list of all files in the Azure Blob Storage container.
        Returns:
            A list of file names.
        """
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blob_list = container_client.list_blobs(include='metadata')
        sas = generate_container_sas(self.account_name, self.container_name, account_key=self.account_key, permission="r", expiry=datetime.now() + timedelta(hours=3))
        files = self.process_blob_list(blob_list, sas)
        return files

    def process_blob_list(self, blob_list, sas):
        """
        Process a list of blobs and return a list of files.
        Args:
            blob_list (list): A list of blobs.
            sas (str): The shared access signature.
        Returns:
            list: A list of files.
        """
        files = []
        converted_files = {}
        for blob in blob_list:
            if not blob.name.startswith('converted/'):
                file = self.create_file_object(blob, sas)
                files.append(file)
            else:
                converted_files[blob.name] = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas}"

        for file in files:
            converted_filename = file.pop('converted_filename', '')
            if converted_filename in converted_files:
                file['converted'] = True
                file['converted_path'] = converted_files[converted_filename]

        return files

    def create_file_object(self, blob, sas):
        """
        Creates a file object with metadata extracted from the given blob.
        Args:
            blob (azure.storage.blob.BlobClient): The blob object.
            sas (str): The shared access signature for the blob.
        Returns:
            dict: The file object with the following properties:
                - filename (str): The name of the file.
                - file_extension (str): The file extension.
                - upload_date (str): The upload date.
                - file_size_kb (str): The file size in kilobytes.
                - converted (bool): Indicates if the file is converted.
                - embeddings_added (bool): Indicates if embeddings are added to the file.
                - chunking_strategy (str): The chunking strategy.
                - chunking_size (str): The chunking size.
                - chunking_overlap (str): The chunking overlap.
                - loading_strategy (str): The loading strategy.
                - user_name (str): The name of the user who uploaded the file.
                - fullpath (str): The full URL of the file including the shared access signature.
                - converted_filename (str): The name of the converted file.
                - converted_path (str): The path of the converted file.
        """
        file = {
            "filename": blob.name,
            "file_extension": blob.metadata.get('file_extension', '') if blob.metadata else '',
            "upload_date": blob.metadata.get('upload_date', '') if blob.metadata else '',
            "file_size_kb": blob.metadata.get('file_size_kb', '') if blob.metadata else '',
            "converted": blob.metadata.get('converted', 'false') == 'true' if blob.metadata else False,
            "embeddings_added": blob.metadata.get('embeddings_added', 'false') == 'true' if blob.metadata else False,
            "chunking_strategy": blob.metadata.get('chunking_strategy', '') if blob.metadata else '',
            "chunking_size": blob.metadata.get('chunking_size', '') if blob.metadata else '',
            "chunking_overlap": blob.metadata.get('chunking_overlap', '') if blob.metadata else '',
            "loading_strategy": blob.metadata.get('loading_strategy', '') if blob.metadata else '',
            "user_name": blob.metadata.get('user_name', '') if blob.metadata else '',
            "fullpath": f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas}",
            "converted_filename": blob.metadata.get('converted_filename', '') if blob.metadata else '',
            "converted_path": ""
        }
        return file

    def get_all_files_by_user_id(self, user_id: str) -> list:
        """
        Retrieves a list of all files associated with a given user ID.
        Args:
            user_id (str): The ID of the user.
        Returns:
            list: A list of file names associated with the user ID.
        """
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blob_list = container_client.walk_blobs(f"{user_id}/", delimiter='/')
        files = []

        for blob in blob_list:
            blobs_in_blob = container_client.walk_blobs(name_starts_with=blob.name, delimiter='/')
            for file in blobs_in_blob:
                files.append(file.name)

        return files

    def upsert_blob_metadata(self, file_name, metadata):
        """
        Upserts the metadata of a blob in Azure Blob Storage.
        Args:
            file_name (str): The name of the blob file.
            metadata (dict): The metadata to be upserted.
        Returns:
            None
        """
        blob_client = BlobServiceClient.from_connection_string(self.connect_str).get_blob_client(container=self.container_name, blob=file_name)
        blob_metadata = blob_client.get_blob_properties().metadata
        blob_metadata.update(metadata)
        blob_client.set_blob_metadata(metadata=blob_metadata)

    def get_container_sas(self):
        """
        Generates a shared access signature (SAS) for the container.

        Returns:
            str: The container SAS.
        """
        return "?" + generate_container_sas(account_name= self.account_name, container_name= self.container_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=1))

    def get_blob_sas(self, file_name):
        """
        Generates a shared access signature (SAS) URL for the specified blob.
        Args:
            file_name (str): The name of the blob file.
        Returns:
            str: The SAS URL for the specified blob.
        """
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}" + "?" + generate_blob_sas(account_name= self.account_name, container_name=self.container_name, blob_name= file_name, account_key= self.account_key, permission='r', expiry=datetime.utcnow() + timedelta(hours=1))

    def prepare_blob(self, user_id: str, data_json: str, blob_name: str):
        """
        Prepares and uploads a JSON file to Azure Blob Storage.
        Args:
            user_id (str): The user ID.
            data_json (str): The JSON data to be uploaded.
            blob_name (str): The name of the blob.
        Returns:
            None
        """
        now = datetime.now()
        parent_folder_name = user_id
        subfolder_name = now.strftime("%Y-%m-%d_%H-%M-%S")
        parent_folder_blob_name = parent_folder_name + '/'
        subfolder_blob_name = parent_folder_blob_name + subfolder_name + '/'
        file_path = f"{blob_name}"
        file_blob_name = subfolder_blob_name + file_path
        data_json = data_json.encode('utf-8')
        self.upload_json_to_azure_storage_account(file_blob_name, data_json)

    def upload_json_to_azure_storage_account(self, file_blob_name: str, data: bytes):
        """
        Uploads a JSON file to an Azure Storage Account.
        Args:
            file_blob_name (str): The name of the file blob.
            data (bytes): The data to be uploaded as bytes.
        Returns:
            None
        """
        blob_service_client = BlobServiceClient(account_url=f"https://{self.account_name}.blob.core.windows.net", credential=self.account_key)
        container_client = blob_service_client.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client(file_blob_name + ".json")
        blob_client.upload_blob(data, overwrite=True)

    def upload_blob_file(self, bytes_data: bytes, uploaded_file_name: str, content_type: Optional[str] = None, user_id: Optional[str] = None):
        """
        Uploads a file to Azure Blob Storage.
        Args:
            bytes_data (bytes): The file data as bytes.
            uploaded_file_name (str): The name of the uploaded file.
            content_type (str, optional): The content type of the file. If not provided, it will be guessed based on the file name. Defaults to None.
            user_id (str, optional): The ID of the user. Defaults to None.
        Raises:
            ValueError: If the required account name, account key, or container name is not provided.
        Returns:
            str: The URL of the uploaded file.
        """
        if content_type == None:
            content_type = mimetypes.MimeTypes().guess_type(uploaded_file_name)[0]
            charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
            content_type = content_type if content_type != None else 'text/plain'

        if self.account_name == None or self.account_key == None or self.container_name == None:
            raise ValueError("Please provide values for AZURE_BLOB_ACCOUNT_NAME, AZURE_BLOB_ACCOUNT_KEY and AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME or AZURE_BLOB_LOCAL_DOCUMENTS_CONTAINER_NAME")

        connect_str = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
        blob_service_client : BlobServiceClient = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=uploaded_file_name)
        blob_client.upload_blob(bytes_data, overwrite=True, content_settings=ContentSettings(content_type=content_type+charset))
