import os
import json
from .AzureSearchHelper import AzureSearchHelper
from .AzureBlobStorageHelper import AzureBlobStorageClient
import urllib.parse

def process_metadata(result):
    metadata_dict = json.loads(result['metadata'])
    processed_metadata = {}
    for key, value in metadata_dict.items():
        if key not in ['id', 'source', 'chunk', 'offset', 'page_number']:
            processed_metadata[key] = value
    if 'title' in processed_metadata:
        processed_metadata['title'] = processed_metadata['title'].replace(
            os.getenv("AZURE_BLOB_GLOBAL_DOCUMENTS_CONTAINER_NAME"), "").strip('/')
    return processed_metadata

class ExploreData:
    def __init__(self) -> None:
        """
        No additional initialization is required at this time.
        """
        pass

    def get_index_metadata(self, explored_index):
        vector_store_helper = AzureSearchHelper(index_name=explored_index)
        search_client = vector_store_helper.get_vector_store().client
        results = search_client.search("*", select="metadata", include_total_count=True)

        index_metadata = []
        if results.get_count() != 0:
            processed_keys = set()

            for result in results:
                processed_metadata = process_metadata(result)
                metadata_key = tuple(sorted(processed_metadata.items()))
                if metadata_key not in processed_keys:
                    processed_keys.add(metadata_key)
                    index_metadata.append(processed_metadata)

        return index_metadata

    def get_blob_metadata(self, container_name):
        blob_client = AzureBlobStorageClient(container_name=container_name)
        return blob_client.get_all_files()

    def merge_metadata(self, index_metadata, blob_metadata):
        meta_dict = {meta["filename"]: meta for meta in blob_metadata}
        for item in index_metadata:
            meta_item = meta_dict.get(item["title"])
            if meta_item:
                item["file_extension"] = meta_item["file_extension"]
                item["upload_date"] = meta_item["upload_date"]
                item["file_size_kb"] = meta_item["file_size_kb"]
                item["chunking_strategy"] = meta_item["chunking_strategy"]
                item["chunking_size"] = meta_item["chunking_size"]
                item["chunking_overlap"] = meta_item["chunking_overlap"]
                item["loading_strategy"] = meta_item["loading_strategy"]
                item["user_name"] = urllib.parse.unquote(meta_item["user_name"])

        return index_metadata