import os
from dotenv import load_dotenv
from doc_intelligence import DocumentIntelligenceService
from openai_service import OpenAIService
from files_storage import FilesStorage


# take environment variables from ../.env.
load_dotenv("../.env")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

def main():
    files_storage = FilesStorage()
    # files_storage.delete_old_todos()
    # files_storage.copy_source_to_todo()
    payslip_files = files_storage.get_todo_files()
    doc_intelligence = DocumentIntelligenceService(AZURE_DOCUMENT_INTELLIGENCE_KEY, AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT)
    openai_service = OpenAIService()
    for payslip_file in payslip_files:
        print(f"Processing {payslip_file}")
        file_text = doc_intelligence.analyze_layout_from_file(payslip_file.path)
        print(file_text)
        payslip_file.new_file_name = openai_service.generate_new_filename(file_text, payslip_file.name)
        payslip_file.new_file_path = files_storage.rename_file(payslip_file.path, payslip_file.new_file_name)
        files_storage.move_file_to_processed(payslip_file.new_file_path)

if __name__ == '__main__':
    main()