# import libraries
import base64
import os
from azure.core.credentials import AzureKeyCredential
# from azure.ai.documentintelligence import DocumentIntelligenceClient
# from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class DocumentIntelligenceService:
    def __init__(self, key, endpoint):
        self.key = key 
        self.endpoint = endpoint  # "https://docintpavelpweurope.cognitiveservices.azure.com/"
        self.credential = AzureKeyCredential(key=key)
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=self.credential)
        
    def get_text_from_image(self, content):
        poller = self.client.begin_analyze_document("prebuilt-read", document=content)
        result = poller.result()
        result_content = result.content
        return result_content

    def analyze_layout_from_file(self, file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        return self.get_text_from_image(content)

#    def analyze_layout_from_blob(self, container_name, blob_name):
        # blob_service = FilesBlobService()
        # content = blob_service.get_file_content(container_name, blob_name)
        # return self.analyze_layout(content)

    def analyze_layout_from_base64(self, base64_str):
        content = base64.b64decode(base64_str)
        return self.get_text_from_image(content)