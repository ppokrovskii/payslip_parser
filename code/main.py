import os
from dotenv import load_dotenv
from files_storage import FilesStorage


# take environment variables from ../.env.
load_dotenv("../.env")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

if __name__ == '__main__':
    files_storage = FilesStorage()
    files_storage.delete_old_results()
    files_storage.copy_source_to_results()
    payslip_files = files_storage.get_files()
    print(payslip_files)